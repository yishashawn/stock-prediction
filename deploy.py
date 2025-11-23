#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deploy to GitHub Pages - Wrapper script
"""

import os
import sys

# Add Git to PATH
git_bin = r"C:\Program Files\Git\bin"
git_cmd = r"C:\Program Files\Git\cmd"
if git_bin not in os.environ.get('Path', ''):
    os.environ['Path'] = os.environ.get('Path', '') + f';{git_bin};{git_cmd}'

# Import and run the deployment script
script_dir = os.path.dirname(os.path.abspath(__file__))
deploy_script = os.path.join(script_dir, "部署到GitHub_Pages.py")

if not os.path.exists(deploy_script):
    print(f"错误: 未找到部署脚本: {deploy_script}")
    sys.exit(1)

# Execute the deployment script using subprocess
import subprocess
result = subprocess.run([sys.executable, deploy_script])
sys.exit(result.returncode)

