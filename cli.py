import argparse
import requests

def main():
    parser = argparse.ArgumentParser(description="CLI for speech-sep-transcribe service")
    parser.add_argument("file", help="Path to audio file")
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default=None)
    args = parser.parse_args()

    url = "http://localhost:8000/v1/transcribe"
    with open(args.file, "rb") as f:
        files = {"file": f}
        data = {"params": f'{{"model":"{args.model}","language":"{args.language}"}}'}
        response = requests.post(url, files=files, data=data)
        print(response.json())

if __name__ == "__main__":
    main()