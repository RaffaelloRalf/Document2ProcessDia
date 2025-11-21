# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  channel = "stable-24.05"; 
  
  packages = [
    # 1. Python & Package Manager
    pkgs.python311  # Python 3.11 Environment
    pkgs.uv         # fast Paket-Manager
    pkgs.gnumake
    
    # 2. System Tools
    pkgs.git
    pkgs.curl
    
    # 3. Mermaid CLI 
    #Install mmdc including Chromium and all Linux libraries.
    pkgs.mermaid-cli
  ];
  
  # Setting Environment Variables
  env = {
    # Prevents npm packages from attempting to load a broken Chrome
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD = "true";
    # Sets the path for your script correctly
    MERMAID_CLI_PATH = "mmdc";
  };
  
  idx = {
    # Useful Extensions for Python & Gemini
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
    ];
    
    previews = {
      enable = true;
      previews = {};
    };
    
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        install-dependencies = "cd process-analysis-agent && uv venv && uv pip install -r requirements.txt";
        default.openFiles = [ "process-analysis-agent/app/agent.py" "README.md" ];
      };
      
      onStart = {
        # Optional
        # check-env = "cd process-analysis-agent && uv pip install -r requirements.txt";
      };
    };
  };
}