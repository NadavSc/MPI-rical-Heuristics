import os
import re

from files_parser import load_file, line_endings_correction, del_comments, comment_in_ranges
from repos_parser import make_dst_folder, FORTRAN_EXTENSIONS


def write_to_file(dst, lines, name, ext):
    make_dst_folder(dst)
    with open(os.path.join(os.path.split(dst)[0], f'{name}_sliced{ext}'), "w") as f:
        f.write(lines)


def find_init_final(lines, ext, rm_comments=True):
    if rm_comments:
        lines = del_comments(lines, ext)
    init_match = re.search(r'[n]\s*[a-z^n]*\s*MPI_Init.*?[\\]*[\\][n]', lines, flags=re.IGNORECASE)
    finalize_matches = [match for match in re.finditer(r'MPI_Finalize[^\\]*', lines, flags=re.IGNORECASE)]
    return lines, init_match, finalize_matches


def init_final_slice(path, dst, rm_comments=True):
    lines, name, ext = load_file(path, load_by_line=False)
    lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments)
    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
        lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
        lines = line_endings_correction(lines)
        write_to_file(dst, lines, name, ext)
        return True
    return False