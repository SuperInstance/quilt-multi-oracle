def fnv1a_64(s):
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h = h ^ b
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

if __name__ == "__main__":
    h = fnv1a_64("café Δ 日本語")
    print(f"0x{h:016x}")
    assert h == 0x024a555471370b18d, "canary failed"
    print("✓ Fleet canary verified")
