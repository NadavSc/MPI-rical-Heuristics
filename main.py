import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'repos_parser'))
sys.path.append(os.path.join(project_path, 'files_parser'))
sys.path.append(os.path.join(project_path, 'c_parse'))


from queries import functions_finder, ast_generator
from queries_multiprocess import openmp_mpi_count_multiprocess, init_finalize_count_multiprocess, functions_finder_multiprocess, program_division_multiprocess
from database import db_origin_generate
from repos_parser import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR
from repos_parser import load_json
from c_parse import repo_parser, Extractor
from program import init_folder, copy_files

from logger import set_logger, info


set_logger()


def program_division(origin_db, functions_db):
    for user_id, user in origin_db.items():
        for repo_id, repo_details in user['repos'].items():
            repo_name, repo_dir = repo_details['name'], repo_details['path']
            programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, user['name'])
            programs_repo_dir = os.path.join(programs_user_dir, repo_name)
            mains, real_headers, _ = repo_parser(repo_dir)
            if mains and not os.path.exists(programs_user_dir):
                os.makedirs(programs_user_dir)
            for main_name, main_path in mains.items():
                extractor = Extractor(main_path, main_name, real_headers)
                extractor.extraction(main_path)
                headers_path = extractor.headers
                c_files_path = extractor.c_files(functions_db, repo_dir, headers_path)
                id, program_path = init_folder(programs_repo_dir)
                copy_files(id, repo_name, headers_path, c_files_path, program_path, main_path, repo_dir)


programs_db = load_json(os.path.join('DB', 'database_programs.json'))
ast_generator(programs_db)