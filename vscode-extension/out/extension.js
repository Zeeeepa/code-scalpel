"use strict";
/**
 * Code Scalpel VS Code Extension
 *
 * MCP server integration for AI-powered code analysis, security scanning,
 * and intelligent refactoring.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
let serverProcess = null;
let outputChannel;
let statusBarItem;
function activate(context) {
    outputChannel = vscode.window.createOutputChannel('Code Scalpel');
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'codeScalpel.showStatus';
    context.subscriptions.push(statusBarItem);
    updateStatusBar('stopped');
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('codeScalpel.startServer', startServer), vscode.commands.registerCommand('codeScalpel.stopServer', stopServer), vscode.commands.registerCommand('codeScalpel.analyzeFile', analyzeCurrentFile), vscode.commands.registerCommand('codeScalpel.securityScan', securityScanProject), vscode.commands.registerCommand('codeScalpel.showStatus', showStatus));
    // Auto-start if configured
    const config = vscode.workspace.getConfiguration('codeScalpel');
    if (config.get('autoStart')) {
        startServer();
    }
    outputChannel.appendLine('Code Scalpel extension activated');
}
function deactivate() {
    if (serverProcess) {
        stopServer();
    }
}
function updateStatusBar(status) {
    switch (status) {
        case 'running':
            statusBarItem.text = '$(check) Code Scalpel';
            statusBarItem.tooltip = 'Code Scalpel MCP Server Running';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'stopped':
            statusBarItem.text = '$(circle-slash) Code Scalpel';
            statusBarItem.tooltip = 'Code Scalpel MCP Server Stopped';
            statusBarItem.backgroundColor = undefined;
            break;
        case 'error':
            statusBarItem.text = '$(error) Code Scalpel';
            statusBarItem.tooltip = 'Code Scalpel MCP Server Error';
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }
    statusBarItem.show();
}
async function startServer() {
    if (serverProcess) {
        vscode.window.showInformationMessage('Code Scalpel server is already running');
        return;
    }
    const config = vscode.workspace.getConfiguration('codeScalpel');
    const pythonPath = config.get('pythonPath') || 'python';
    const port = config.get('serverPort') || 8765;
    const tier = config.get('tier') || 'community';
    const licensePath = config.get('licensePath') || '';
    const env = { ...process.env };
    if (tier !== 'community') {
        env['CODE_SCALPEL_TIER'] = tier;
    }
    if (licensePath) {
        env['CODE_SCALPEL_LICENSE_PATH'] = licensePath;
    }
    try {
        // Start the MCP server
        serverProcess = (0, child_process_1.spawn)(pythonPath, [
            '-m', 'code_scalpel.mcp.server',
            '--port', port.toString()
        ], {
            env,
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
        });
        serverProcess.stdout?.on('data', (data) => {
            outputChannel.appendLine(`[stdout] ${data}`);
        });
        serverProcess.stderr?.on('data', (data) => {
            outputChannel.appendLine(`[stderr] ${data}`);
        });
        serverProcess.on('error', (err) => {
            outputChannel.appendLine(`[error] ${err.message}`);
            updateStatusBar('error');
            vscode.window.showErrorMessage(`Failed to start Code Scalpel server: ${err.message}`);
            serverProcess = null;
        });
        serverProcess.on('exit', (code) => {
            outputChannel.appendLine(`[exit] Server exited with code ${code}`);
            updateStatusBar('stopped');
            serverProcess = null;
        });
        updateStatusBar('running');
        vscode.window.showInformationMessage(`Code Scalpel MCP server started on port ${port}`);
        outputChannel.appendLine(`Server started on port ${port} (tier: ${tier})`);
    }
    catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Failed to start Code Scalpel server: ${message}`);
        updateStatusBar('error');
    }
}
async function stopServer() {
    if (!serverProcess) {
        vscode.window.showInformationMessage('Code Scalpel server is not running');
        return;
    }
    serverProcess.kill();
    serverProcess = null;
    updateStatusBar('stopped');
    vscode.window.showInformationMessage('Code Scalpel server stopped');
    outputChannel.appendLine('Server stopped');
}
async function analyzeCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active file to analyze');
        return;
    }
    const filePath = editor.document.uri.fsPath;
    const config = vscode.workspace.getConfiguration('codeScalpel');
    const pythonPath = config.get('pythonPath') || 'python';
    outputChannel.appendLine(`Analyzing file: ${filePath}`);
    outputChannel.show();
    try {
        const result = (0, child_process_1.spawn)(pythonPath, [
            '-m', 'code_scalpel.cli',
            'analyze',
            filePath
        ], {
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
        });
        let output = '';
        result.stdout?.on('data', (data) => {
            output += data.toString();
            outputChannel.appendLine(data.toString());
        });
        result.stderr?.on('data', (data) => {
            outputChannel.appendLine(`[stderr] ${data}`);
        });
        result.on('close', (code) => {
            if (code === 0) {
                vscode.window.showInformationMessage('Analysis complete. See Output panel for results.');
            }
            else {
                vscode.window.showWarningMessage(`Analysis completed with exit code ${code}`);
            }
        });
    }
    catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        vscode.window.showErrorMessage(`Analysis failed: ${message}`);
    }
}
async function securityScanProject() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showWarningMessage('No workspace folder open');
        return;
    }
    const projectPath = workspaceFolder.uri.fsPath;
    const config = vscode.workspace.getConfiguration('codeScalpel');
    const pythonPath = config.get('pythonPath') || 'python';
    outputChannel.appendLine(`Security scanning project: ${projectPath}`);
    outputChannel.show();
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Code Scalpel: Security Scan',
        cancellable: true
    }, async (progress, token) => {
        return new Promise((resolve, reject) => {
            const result = (0, child_process_1.spawn)(pythonPath, [
                '-m', 'code_scalpel.cli',
                'security-scan',
                projectPath
            ], {
                cwd: projectPath
            });
            token.onCancellationRequested(() => {
                result.kill();
                resolve();
            });
            result.stdout?.on('data', (data) => {
                outputChannel.appendLine(data.toString());
                progress.report({ message: 'Scanning...' });
            });
            result.stderr?.on('data', (data) => {
                outputChannel.appendLine(`[stderr] ${data}`);
            });
            result.on('close', (code) => {
                if (code === 0) {
                    vscode.window.showInformationMessage('Security scan complete. See Output panel for results.');
                }
                else {
                    vscode.window.showWarningMessage(`Security scan completed with issues. See Output panel.`);
                }
                resolve();
            });
            result.on('error', (err) => {
                vscode.window.showErrorMessage(`Security scan failed: ${err.message}`);
                reject(err);
            });
        });
    });
}
async function showStatus() {
    const status = serverProcess ? 'Running' : 'Stopped';
    const config = vscode.workspace.getConfiguration('codeScalpel');
    const tier = config.get('tier') || 'community';
    const port = config.get('serverPort') || 8765;
    const message = `Code Scalpel Status:
- Server: ${status}
- Port: ${port}
- Tier: ${tier}`;
    const action = await vscode.window.showInformationMessage(message, serverProcess ? 'Stop Server' : 'Start Server', 'View Output');
    if (action === 'Stop Server') {
        await stopServer();
    }
    else if (action === 'Start Server') {
        await startServer();
    }
    else if (action === 'View Output') {
        outputChannel.show();
    }
}
//# sourceMappingURL=extension.js.map