# ---------- app.py (主程序入口) ----------
from flask import Flask, request, jsonify, render_template, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis.cluster import RedisCluster, ClusterNode
import ast
import re
import astunparse
import hashlib
import redis


# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secure_secret_key_here'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# 连接Redis集群（示例配置）
# 替换掉原来的 dict 形式
startup_nodes = [
    ClusterNode("127.0.0.1", 7000),
    ClusterNode("127.0.0.1", 7001)
]


# 初始化单机Redis客户端（供其他地方使用）
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 初始化Limiter，使用单机Redis的URI即可
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["10000 per second"]  # 或你需要的限流策略
)
class CodeAnalyzer:
    def __init__(self):
        self.rules = [
            self._check_syntax,
            self._detect_infinite_loops,
            self._check_naming_convention,
            self._detect_hardcoded_credentials,
            self._check_security_issues
        ]

    def full_analysis(self, code):
        """执行完整的代码分析"""
        diagnostics = []
        try:
            tree = ast.parse(code)
            for rule in self.rules:
                diagnostics.extend(rule(code, tree))
        except Exception as e:
            app.logger.error(f"分析错误: {str(e)}")
        return diagnostics

    def _check_syntax(self, code, tree):
        """语法检查"""
        try:
            ast.parse(code)
            return []
        except SyntaxError as e:
            return [self._create_issue(e.lineno, e.offset, f"语法错误：{e.msg}", "critical")]

    def _detect_infinite_loops(self, code, tree):
        """检测危险循环"""
        issues = []
        pattern = r'(while\s+True\s*:|for\s+.+\s+in\s+.+\s*:\s*pass)'
        for lineno, line in enumerate(code.split('\n'), 1):
            if re.search(pattern, line):
                issues.append(self._create_issue(lineno, 0, "可能存在无限循环", "warning"))
        return issues

    def _check_naming_convention(self, code, tree):
        """检查命名规范"""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append(self._create_issue(
                        node.lineno, node.col_offset,
                        "函数命名不符合蛇形命名规范", "warning"
                    ))
        return issues

    def _detect_hardcoded_credentials(self, code, tree):
        """检测硬编码凭证"""
        credential_patterns = [
            r'password\s*=\s*[\'"].+[\'"]',
            r'api_key\s*=\s*[\'"].+[\'"]'
        ]
        issues = []
        for pattern in credential_patterns:
            for match in re.finditer(pattern, code):
                issues.append(self._create_issue(
                    code[:match.start()].count('\n') + 1,
                    match.start() - code.rfind('\n', 0, match.start()),
                    "检测到硬编码的敏感信息", "high"
                ))
        return issues

    def _check_security_issues(self, code, tree):
        """安全检查"""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute) and
                    node.func.attr == 'execute' and
                    any(isinstance(arg, ast.Add) for arg in node.args)):
                    issues.append(self._create_issue(
                        node.lineno, node.col_offset,
                        "潜在的SQL注入风险", "high"
                    ))
        return issues

    def _create_issue(self, line, column, message, severity):
        return {
            "line": line,
            "column": column,
            "message": message,
            "severity": severity,
            "id": hashlib.md5(f"{line}:{column}:{message}".encode()).hexdigest()
        }

def generate_highlighted_html(code, diagnostics):
    """生成带高亮标记的HTML"""
    lines = code.split('\n')
    for diag in sorted(diagnostics, key=lambda x: x['line'], reverse=True):
        line_num = diag['line'] - 1
        if 0 <= line_num < len(lines):
            lines[line_num] = (
                f'<div class="code-line {diag["severity"]}" data-diagnostic="{diag["id"]}">'
                f'<span class="line-number">{diag["line"]}</span>'
                f'<span class="code-content">{lines[line_num]}</span>'
                f'<div class="tooltip">{diag["message"]}</div></div>'
            )
    return '\n'.join(lines)

# ---------- 路由定义 ----------
@app.route('/')
@limiter.limit("60/minute")
def index():
    """主界面"""
    session['user'] = 'test_user'  # 假登录
    return render_template('editor.html')

@app.route('/diagnose', methods=['POST'])
@limiter.limit("30000/hour")
def diagnose_code():
    """代码诊断接口"""
    code = request.json.get('code', '')
    if len(code) > 10000:
        return jsonify({"error": "代码超过长度限制"}), 400

    analyzer = CodeAnalyzer()
    diagnostics = analyzer.full_analysis(code)
    highlighted = generate_highlighted_html(code, diagnostics)

    score = calculate_code_quality_score(diagnostics)

    app.logger.info(f"Session 内容: {session}")
    app.logger.info(f"诊断结果: {diagnostics}")

    return jsonify({
        "diagnostics": diagnostics,
        "highlighted": highlighted,
        "score": score
    })
    

@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查Redis连接
        redis_client.ping()
        return jsonify({
            "status": "healthy",
            "components": {
                "redis": "available",
                "database": "available"
            }
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500



# ---------- 辅助函数 ----------
def calculate_code_quality_score(diagnostics):
    """计算代码质量评分"""
    severity_weights = {'critical': 5, 'high': 3, 'warning': 1}
    base_score = 100
    for diag in diagnostics:
        base_score -= severity_weights.get(diag['severity'], 0)
    return max(base_score, 0)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)