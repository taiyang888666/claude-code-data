#!/bin/bash
# Claude Code 记忆和技能还原脚本
# 在新电脑上运行此脚本，自动还原所有记忆、技能、命令和设置

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_HOME="$HOME/.claude"

echo "=== Claude Code 记忆和技能还原 ==="

# 1. 创建目录结构
# 注意：项目路径需要根据新电脑的实际路径调整
PROJECT_KEY=$(echo "$SCRIPT_DIR" | sed 's|/\.claude-sync||' | sed 's|/|-|g' | sed 's|^-||')
MEMORY_DIR="$CLAUDE_HOME/projects/$PROJECT_KEY/memory"

mkdir -p "$MEMORY_DIR"
mkdir -p "$CLAUDE_HOME/skills"
mkdir -p "$CLAUDE_HOME/commands"

# 2. 还原记忆文件
echo "还原记忆文件..."
cp "$SCRIPT_DIR/memory/"*.md "$MEMORY_DIR/" 2>/dev/null && echo "  记忆文件 OK" || echo "  记忆文件跳过"

# 3. 还原技能文件
echo "还原技能文件..."
cp "$SCRIPT_DIR/skills/"*.md "$CLAUDE_HOME/skills/" 2>/dev/null && echo "  技能文件 OK" || echo "  技能文件跳过"

# 4. 还原自定义命令
echo "还原自定义命令..."
cp "$SCRIPT_DIR/commands/"*.md "$CLAUDE_HOME/commands/" 2>/dev/null && echo "  命令文件 OK" || echo "  命令文件跳过"

# 5. 还原设置（如果新电脑没有设置文件）
if [ ! -f "$CLAUDE_HOME/settings.json" ]; then
    echo "还原设置文件..."
    cp "$SCRIPT_DIR/settings/settings.json" "$CLAUDE_HOME/settings.json" 2>/dev/null && echo "  设置文件 OK" || echo "  设置文件跳过"
else
    echo "设置文件已存在，跳过（避免覆盖）"
fi

echo ""
echo "=== 还原完成 ==="
echo "记忆目录: $MEMORY_DIR"
echo "技能目录: $CLAUDE_HOME/skills/"
echo "命令目录: $CLAUDE_HOME/commands/"
echo ""
echo "现在可以在项目目录中运行 'claude' 启动 Claude Code"
