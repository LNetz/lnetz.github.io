# Run the site generator but capture its file writes and print them as JSON (Sophos blocks python writes).
import builtins, io, json, runpy, sys
files, real = {}, builtins.open
class W(io.StringIO):
    def __init__(self, p): super().__init__(); self.p = p
    def close(self):
        if not self.closed: files[str(self.p)] = self.getvalue()
        super().close()
    def __exit__(self, *a): self.close()
def op(p, mode="r", *a, **k):
    return W(p) if "w" in mode else real(p, mode, *a, **k)
builtins.open = op
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))   # the generator imports its sibling modules
out, sys.stdout = sys.stdout, sys.stderr          # the generator's own prints go to stderr
runpy.run_path(sys.argv[1], run_name="__main__")
sys.stdout = out
sys.stdout.buffer.write(json.dumps(files).encode())
