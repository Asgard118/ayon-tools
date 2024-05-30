import json
import logging
import os
from pathlib import Path

from git import Repo, GitCommandError


class GitHelper:
    def __init__(self):
        self.repo_root = os.getenv('AYON_SETTINGS_REPO_ROOT') or Path('~/ayon-settings-root').expanduser()


    def init(self):
        """New repo"""
        if self.repo_root.exists():
            return
        try:
            repo = Repo.init(self.repo_root.as_posix())
            logging.info('New repository initialized')
        except GitCommandError as e:
            logging.exception('repository initialize error')

    def get_studio_path(self, studio_code: str):
        """Get studio path root"""
        return self.repo_root / 'studios' / studio_code

    def get_studio_config(self, studio_name: str) -> dict:
        config_file = self.get_studio_path(studio_name) / 'studio.json'
        if config_file.exists():
            return json.loads(config_file.read_text())
        else:
            return {}

    def set_studio_config(self, studio_code: str, config: dict):
        config_file = self.get_studio_path(studio_code) / 'studio.json'
        config_file.parent.mkdir(parents=True)
        config_file.write_text(json.dumps(config, indent=4))
        return config_file.exists()

    def add_new_studio(self, studio_name: str, studio_code: str):
        studio_path = self.get_studio_path(studio_code)
        if studio_path.exists():
            raise Exception(f'Studio {studio_name} already exists')
        self.set_studio_config(studio_code, dict(
            name=studio_name, code=studio_code
        ))



    def _create_branch(self, branch_name):
        """Создает новую ветку в репозитории"""
        try:
            repo.git.branch(branch_name)
            print(f"Создана новая ветка {branch_name}")
        except GitCommandError as e:
            print(f"Ошибка при создании ветки: {e}")

def switch_branch(repo, branch_name):
    """Переключается на указанную ветку"""
    try:
        repo.git.checkout(branch_name)
        print(f"Переключено на ветку {branch_name}")
    except GitCommandError as e:
        print(f"Ошибка при переключении на ветку: {e}")

def create_commit(repo, message):
    """Создает коммит изменений"""
    try:
        repo.git.add('.')
        repo.git.commit('-m', message)
        print(f"Создан коммит с сообщением: {message}")
    except GitCommandError as e:
        print(f"Ошибка при создании коммита: {e}")

def add_tag(repo, tag_name, commit_hash):
    """Добавляет тег на коммит"""
    try:
        repo.git.tag('-a', tag_name, commit_hash, '-m', f'Tag for commit {commit_hash}')
        print(f"Добавлен тег {tag_name} на коммит {commit_hash}")
    except GitCommandError as e:
        print(f"Ошибка при добавлении тега: {e}")

def merge_branches(repo, branch_name):
    """Мержит ветку в текущую"""
    try:
        repo.git.merge(branch_name)
        print(f"Ветка {branch_name} успешно смержена в текущую ветку")
    except GitCommandError as e:
        print(f"Ошибка при слиянии веток: {e}")

def push_changes(repo):
    """Делает push изменений на сервер"""
    try:
        repo.git.push()
        print("Изменения успешно отправлены на сервер")
    except GitCommandError as e:
        print(f"Ошибка при отправке изменений на сервер: {e}")

def show_diff(repo, file1, file2):
    """Показывает diff между двумя файлами"""
    try:
        diff = repo.git.diff(file1, file2)
        print(diff)
    except GitCommandError as e:
        print(f"Ошибка при показе diff: {e}")

def iterate_branches(repo):
    """Итерирует все ветки репозитория и показывает теги коммитов на каждой ветке"""
    for branch in repo.branches:
        print(f"Ветка: {branch}")
        for commit in repo.iter_commits(branch):
            if commit.tag:
                print(f"  Коммит: {commit.hexsha}, Тег: {commit.tag}")
            else:
                print(f"  Коммит: {commit.hexsha}")