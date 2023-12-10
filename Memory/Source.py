import tkinter as tk
import math

# Constants
MAIN_MEMORY_ACCESS = 120

def hex_to_binary(hex_string):
    return bin(int(hex_string, 16))[2:].zfill(24)

class Address:
    def __init__(self, original, binary_str, index_size, offset_size):
        tag_size = len(binary_str) - index_size - offset_size
        self.hex = original
        self.tag = binary_str[:tag_size]
        self.index = binary_str[tag_size:tag_size + index_size]
        self.offset = binary_str[tag_size + index_size:]

class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = ""
        self.data = ""
        self.index = ""

def create_addresses(index_size, offset_size, file_path):
    addresses = []
    with open(file_path) as file:
        for line in file:
            cells = line.strip().split(',')
            for cell in cells:
                binary_address = hex_to_binary(cell[2:])
                address = Address(cell, binary_address, index_size, offset_size)
                addresses.append(address)
    return addresses

def simulate_cache(S, L, cache_access, file_path, output_text):
    disp_size = int(math.log2(L))
    C = S // L
    indx_size = int(math.log2(C))

    hit_penalty = cache_access
    miss_penalty = cache_access + MAIN_MEMORY_ACCESS

    addresses = create_addresses(indx_size, disp_size, file_path)
    cache = [CacheLine() for _ in range(C)]

    hits = misses = accesses = 0

    for address in addresses:
        output = ""
        n = int(address.index, 2)
        if not cache[n].valid or cache[n].tag != address.tag:
            cache[n].valid = True
            cache[n].tag = address.tag
            cache[n].data = address.offset
            cache[n].index = address.index
            misses += 1
        else:
            hits += 1
        accesses += 1
        hit_ratio = hits / accesses
        miss_ratio = 1 - hit_ratio
        amat = hit_ratio * hit_penalty + miss_ratio * miss_penalty
        output += f"Accessing {address.hex}\n"
        output += f"{'Index':<8}{'Tag':<8} | {'Data':<8}\n"
        for cache_line in cache:
            if cache_line.valid:
                output += f"{cache_line.index:<8}{cache_line.tag:<8} | {cache_line.data:<8}\n"
        output += f"Total Number of accesses: {accesses}\n"
        output += f"Hits ratio: {hit_ratio * 100:.2f}%\n"
        output += f"Misses ratio: {miss_ratio * 100:.2f}%\n"
        output += f"AMAT: {amat:.2f} cycles\n\n"
        output_text.insert(tk.END, output)

def start_simulation(entries, output_text):
    S = int(entries['Cache Size S (bytes)'].get())
    L = int(entries['Cache Line Size L (bytes)'].get())
    cache_access = int(entries['Cache Cycles'].get())
    file_path = entries['Addresses File Path'].get()
    simulate_cache(S, L, cache_access, file_path, output_text)

def makeform(root, fields):
    entries = {}
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[field] = ent
    return entries

if __name__ == '__main__':
    fields = ('Cache Size S (bytes)', 'Cache Line Size L (bytes)', 'Cache Cycles', 'Addresses File Path')
    root = tk.Tk()
    root.title("Cache Simulator")
    ents = makeform(root, fields)
    ents['Addresses File Path'].delete(0, tk.END)
    ents['Addresses File Path'].insert(0, 'Addresses.txt')
    b1 = tk.Button(root, text='Run Simulation',
                   command=(lambda e=ents: start_simulation(e, output_text)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    output_text = tk.Text(root, height=15)
    output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    root.mainloop()