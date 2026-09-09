package architecture

import (
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"runtime"
	"testing"
)

func TestMethodFlowEntryUsesOnlyNamedStages(t *testing.T) {
	assertMethodFlowFile(t, "../adapter/cli/entry.go", "Entry", "Run")
}

func TestMethodFlowUsecaseUsesOnlyNamedStages(t *testing.T) {
	assertMethodFlowFile(t, "../usecase/work/start_work.go", "StartWork", "Run")
}

func TestMethodFlowRejectsDirectExternalCall(t *testing.T) {
	source := `package sample
import "fmt"
type Flow struct{}
func (f *Flow) Run() error {
	f.read()
	fmt.Println("detail")
	return f.write()
}`
	if violations := validateMethodFlow([]byte(source), "Flow", "Run"); len(violations) == 0 {
		t.Fatal("外部処理の直接呼び出しを検出できませんでした")
	}
}

func assertMethodFlowFile(t *testing.T, relativePath, receiverType, methodName string) {
	t.Helper()
	_, currentFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("検査ファイルの場所を取得できません")
	}
	source, err := os.ReadFile(filepath.Join(filepath.Dir(currentFile), relativePath))
	if err != nil {
		t.Fatal(err)
	}
	if violations := validateMethodFlow(source, receiverType, methodName); len(violations) != 0 {
		t.Fatalf("%s.%s: %v", receiverType, methodName, violations)
	}
}

func validateMethodFlow(source []byte, receiverType, methodName string) []string {
	file, err := parser.ParseFile(token.NewFileSet(), "flow.go", source, 0)
	if err != nil {
		return []string{"Goの構文を読めません: " + err.Error()}
	}
	method, receiverName := findMethod(file, receiverType, methodName)
	if method == nil {
		return []string{receiverType + "." + methodName + " がありません"}
	}

	stageCalls := 0
	violations := make([]string, 0)
	ast.Inspect(method.Body, func(node ast.Node) bool {
		call, ok := node.(*ast.CallExpr)
		if !ok {
			return true
		}
		selector, ok := call.Fun.(*ast.SelectorExpr)
		if !ok {
			violations = append(violations, "名前のない関数を直接呼んでいます")
			return true
		}
		owner, ok := selector.X.(*ast.Ident)
		if !ok || owner.Name != receiverName {
			violations = append(violations, "外部処理を直接呼んでいます")
			return true
		}
		stageCalls++
		return true
	})
	if stageCalls == 0 {
		violations = append(violations, "利用の流れを示す段がありません")
	}
	return violations
}

func findMethod(file *ast.File, receiverType, methodName string) (*ast.FuncDecl, string) {
	for _, declaration := range file.Decls {
		method, ok := declaration.(*ast.FuncDecl)
		if !ok || method.Recv == nil || method.Name.Name != methodName || len(method.Recv.List) != 1 {
			continue
		}
		if typeName(method.Recv.List[0].Type) != receiverType || len(method.Recv.List[0].Names) != 1 {
			continue
		}
		return method, method.Recv.List[0].Names[0].Name
	}
	return nil, ""
}

func typeName(expression ast.Expr) string {
	switch value := expression.(type) {
	case *ast.Ident:
		return value.Name
	case *ast.StarExpr:
		return typeName(value.X)
	default:
		return ""
	}
}
