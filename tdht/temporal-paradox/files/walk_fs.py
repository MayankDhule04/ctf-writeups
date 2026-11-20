import ext4

f = open('Temporal Paradox/gateway_snapshot.img', 'rb')
vol = ext4.Volume(f)

def walk(inode, path, depth=0):
    if depth > 20:
        return
    try:
        entries = list(inode.opendir())
    except Exception as e:
        return
    for de, ftype in entries:
        name = de.name_str
        if name in ('.', '..'):
            continue
        full = path + '/' + name
        child = vol.inode_at(de.inode)
        size = child.i_size
        is_dir = (ftype == ext4.enums.EXT4_FT.DIR) if hasattr(ext4,'enums') else (int(ftype) == 2)
        print(f"{full}\t{size}\t{'DIR' if is_dir else str(ftype)}\tino={de.inode}")
        if is_dir:
            walk(child, full, depth+1)

walk(vol.root, '')
