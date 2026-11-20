from setuptools import setup, find_packages

setup(
    name="ctf-tool",
    version="1.0.0",
    description="Unified CTF Solver Tool — auto-detect & solve crypto/web/forensics/stego challenges",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ctf_tool=ctf_tool.cli:main",
        ],
    },
    install_requires=[
        "requests>=2.28.0",
        "pycryptodome>=3.19.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "colorama>=0.4.6",
        "PyJWT>=2.8.0",
    ],
    python_requires=">=3.8",
)
