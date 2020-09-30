import json
import os
import requests
import subprocess
import sys

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtention(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the "
                "following extentions: "
                ", ".join(e.name for e in self.extensions)
            )

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            "-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY=" + extdir,
            "-DPYTHON_EXECUTABLE=" + sys.executable,
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
        build_args += ["--", "-j2"]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )


def get_version(release_override="0.0.1"):
    def get_last_version_root(last_version):
        if ".post" in last_version or ".dev" in last_version:
            last_version_root = ".".join(last_version.split(".")[:-1])
        else:
            last_version_root = last_version
        return last_version_root

    cwd = os.path.dirname(os.path.realpath(__file__))
    git_version = subprocess.check_output(
        ["git", "describe", "--always", "--tags"], stderr=None, cwd=cwd
    ).strip().decode("utf-8")

    if "." not in git_version:
        # Git doesn't know about a tag yet, so set the version root to release_override
        version_root = release_override
    else:
        version_root = git_version.split("-")[0]

    if "." not in git_version or "-" in git_version:
        # This commit doesn't correspond to a tag, so mark it as post or dev
        response = requests.get(
            "https://test.pypi.org/pypi/parametric-plasma-source/json"
        )
        if response.status_code == 200:
            # Response from TestPyPI was successful - get latest version and increment
            last_version = json.loads(response.content)["info"]["version"]
            last_version_root = get_last_version_root(last_version)

            if last_version_root == version_root:
                # We're still on the same released version, so increment the 'post'
                post_count = 1
                if "post" in last_version:
                    post_index = last_version.rfind("post") + 4
                    post_count = int(last_version[post_index:])
                    post_count += 1
                version = version_root + ".post" + str(post_count)
            else:
                response = requests.get(
                    "https://pypi.org/pypi/parametric-plasma-source/json"
                )
                dev_count = 1
                if response.status_code == 200:
                    # Response from PyPI was successful - get dev version and increment
                    last_version = json.loads(response.content)["info"]["version"]
                    last_version_root = get_last_version_root(last_version)

                    if last_version_root == version_root:
                        if "dev" in last_version:
                            dev_index = last_version.rfind("dev") + 3
                            dev_count = int(last_version[dev_index:])
                            dev_count += 1
                version = version_root + ".dev" + str(dev_count)
        else:
            # Bad response from TestPyPI, so use git commits (requires git history)
            # NOTE: May cause version clashes on mutliple branches - use test.pypi
            # to avoid this.
            num_commits = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"], stderr=None, cwd=cwd
            ).strip().decode("utf-8")
            version = release_override + ".post" + num_commits
    else:
        version = version_root
    return version


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="parametric_plasma_source",
    version=get_version("0.0.6"),
    author="Andrew Davis",
    author_email="jonathan.shimwell@ukaea.uk",
    description="Parametric plasma source for fusion simulations in OpenMC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/makeclean/parametric-plasma-source/",
    packages=find_packages(),
    ext_modules=[CMakeExtention("parametric_plasma_source/plasma_source")],
    package_data={"parametric_plasma_source": ["source_sampling.so"]},
    cmdclass=dict(build_ext=CMakeBuild),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
