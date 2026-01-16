#!/usr/bin/env python3
"""
Helper to check Ollama and optionally pull a Hugging Face model into Ollama.
Usage:
  python3 tools/setup_ollama_model.py --model AlicanKiraz0/Cybersecurity-BaronLLM_Offensive_Security_LLM_Q6_K_GGUF

The script will:
- Check if Ollama daemon is reachable at localhost:11434 (or OLLAMA_API_BASE)
- List existing models and report whether the requested model is present
- If not present and the `ollama` CLI is available, attempt to `ollama pull <model>`
  (this requires Ollama >= supported version and internet access)
- Print the env var you should set (`OLLAMA_MODEL_NAME`) and an example `export` line

Note: Pulling large GGUF models may take time and disk space.
"""

import argparse
import os
import requests
import shutil
import subprocess
import sys
from urllib.parse import urljoin

DEFAULT_API = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")


def list_ollama_models(api_base: str):
    try:
        r = requests.get(urljoin(api_base, "/v1/models"), timeout=3)
        r.raise_for_status()
        try:
            data = r.json()
        except Exception:
            # Fall back to raw text; try to interpret as JSON string
            text = r.text.strip()
            try:
                data = json.loads(text)
            except Exception:
                return [text]

        # Normalize to a list of model descriptors
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("models", "data", "items"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If it's a mapping of id->meta, convert to list
            try:
                return [{"id": k, **(v if isinstance(v, dict) else {"info": v})} for k, v in data.items()]
            except Exception:
                return [data]
        # Unknown type; return as single-item list
        return [data]
    except Exception as e:
        print(f"Could not reach Ollama API at {api_base}: {e}")
        return None


def cli_available(name="ollama"):
    return shutil.which(name) is not None


def pull_model_cli(model_spec: str):
    # Call: ollama pull <model_spec>
    try:
        print(f"Running: ollama pull {model_spec} (this may take a while)...")
        subprocess.check_call(["ollama", "pull", model_spec])
        return True
    except subprocess.CalledProcessError as e:
        print(f"ollama pull failed: {e}")
        return False
    except FileNotFoundError:
        print("ollama CLI not found on PATH.")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=False, help="Hugging Face model id or Ollama model alias")
    p.add_argument("--local", required=False, help="Path to local GGUF file to import into Ollama")
    p.add_argument("--alias", required=False, help="Alias/name to give the imported Ollama model (e.g. 'baron')")
    args = p.parse_args()

    model = args.model
    local_path = args.local
    alias = args.alias or "baron"

    if local_path:
        print(f"Importing local model file into Ollama: {local_path} as alias '{alias}'")
        if not os.path.exists(local_path):
            print(f"Local file not found: {local_path}")
            sys.exit(1)
        if not cli_available():
            print("ollama CLI not available on PATH; cannot import local file automatically.")
            print(f"Please run: ollama import {local_path} --name {alias}")
            sys.exit(1)
        # Attempt import
        try:
            subprocess.check_call(["ollama", "import", local_path, "--name", alias])
        except subprocess.CalledProcessError as e:
            print(f"ollama import failed: {e}")
            sys.exit(1)
        # After import, set model variable to alias to verify presence
        model = alias

    if not model:
        p.print_help()
        sys.exit(1)

    print(f"Checking Ollama for model: {model}")

    models = list_ollama_models(DEFAULT_API)
    if models is None:
        print("Ollama daemon not reachable.")
        if cli_available():
            print("Ollama CLI is available — you can try pulling the model locally using:")
            print(f"  ollama pull {model}")
        else:
            print("Install and run Ollama, or set up a remote inference endpoint and set DEFAULT_LLM accordingly.")
        sys.exit(1)

    # models is expected to be a list of model descriptors (or strings)
    model_names = []
    for m in models:
        if isinstance(m, dict):
            model_names.append(m.get("id") or m.get("name") or m.get("model") or str(m))
        else:
            model_names.append(str(m))
    print("Installed Ollama models:")
    for m in model_names:
        print(" -", m)

    # Heuristic: if model id present directly, we're good. Otherwise, check repo suffix.
    wanted_alias = None
    if model in model_names:
        wanted_alias = model
    else:
        # Try to find a model that contains the repo name or a short name
        short = model.split('/')[-1]
        for m in model_names:
            if short in (m or ""):
                wanted_alias = m
                break

    if wanted_alias:
        print(f"Found model in Ollama as '{wanted_alias}'. Set:")
        print(f"  export OLLAMA_MODEL_NAME=\"{wanted_alias}\"")
        print("Then run your agents — they will prefer Ollama when this is set.")
        sys.exit(0)

    print(f"Model not present in Ollama: {model}")
    if cli_available():
        print("Attempting to pull using the ollama CLI...")
        ok = pull_model_cli(model)
        if ok:
            print("Pull succeeded — re-run the script to detect the pulled model:")
            print(f"  python3 tools/setup_ollama_model.py --model {model}")
        else:
            print("Pull failed. You may need to provide a different model spec or pull manually.")
    else:
        print("ollama CLI not on PATH. Install Ollama and ensure 'ollama' is runnable from your shell.")
        print("Alternatively, load the GGUF into Ollama manually and set OLLAMA_MODEL_NAME to the model id shown by `ollama ls`.")


if __name__ == '__main__':
    main()
