from setuptools import setup, Extension
from Cython.Build import cythonize
<<<<<<< HEAD
import os, subprocess
=======
import os, subprocess, platform
>>>>>>> f72c0d9 (Changes to setup.py)
import numpy

def configure_extension_module(extension_module: Extension, papi_install_parent_directory: str):
    # Handle PAPI install include directory
    papi_install_include_directory = os.path.join(f"{os.getcwd()}", papi_install_parent_directory, "include")
    extension_module.include_dirs.append(papi_install_include_directory)

    # Handle PAPI install lib directory
    papi_install_lib_directory = os.path.join(f"{os.getcwd()}", papi_install_parent_directory, "lib")
    extension_module.library_dirs.append(papi_install_lib_directory)

    # Handle runtime libraries, this is needed for libpapi.so and libpfm4.so to be found at runtime
    extension_module.runtime_library_dirs.append(papi_install_lib_directory)

def search_environment_variable(environment_path: str):
    for environment_directory in environment_path.split(":"):
        # Cray PAPI is not a true PAPI install ignore entries
        if "cray" in environment_directory:
            continue

        try:
            if "libpapi.so" in os.listdir(environment_directory):
                # Return the parent directory to properly construct the extension module
                return os.path.dirname(environment_directory)
        # Catch FileNotFoundError, but continue on to other directories
        except FileNotFoundError:
            pass

if os.name == "nt":
    raise NotImplementedError("cyPAPI does not support Windows Operating Systems.")


extension_module_papi = Extension( "cypapi.cypapi",
                                   sources = ["cypapi/cypapi.pyx"],
                                   libraries = ["papi", "pfm"],
                                   include_dirs = [numpy.get_include()],
                                   define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")] )

# Search for PAPI installation
# Check to see if a user set PAPI_DIR, this overrides all other options
papi_install_parent_directory = os.environ.get("PAPI_DIR")
if papi_install_parent_directory is None:
     # Preemptively check to see if papi is in the /opt directory, this still remains as the fourth option; however,
     # for workflow purposes this is done here
     opt_path = "/opt"
     papi_in_opt_found = None
     # Search for a papi directory in /opt e.g. papi, papi-7-2-0, etc
     try:
         papi_in_opt_found = next(os.path.join(opt_path, directory) for directory in os.listdir(opt_path) if "papi" in directory)
     # Catch StopIteration, occurs if conditional was not met 
     except StopIteration:
         pass

     # Check LIBRARY_PATH for PAPI installation
     if ( library_path := os.environ.get("LIBRARY_PATH") ) is not None:
         papi_install_parent_directory = search_environment_variable(library_path)
     # Check LD_LIBRARY_PATH for PAPI installation 
     if ( ld_library_path := os.environ.get("LD_LIBRARY_PATH") ) is not None and papi_install_parent_directory is None:
         papi_install_parent_directory = search_environment_variable(ld_library_path)
     # Check /opt/ for PAPI installation
     if papi_in_opt_found is not None and papi_install_parent_directory is None:
         find_command = f"find {papi_in_opt_found} -type d -exec test -e '{{}}'/bin -a -e '{{}}'/include -a -e '{{}}'/lib -a -e '{{}}'/share \; -print"
         completed_process = subprocess.run(find_command, shell = True, check = True, capture_output = True, universal_newlines = True)
         # It is possible that we could find multiple PAPI installation directories, just take the first one
         papi_install_parent_directory = completed_process.stdout.split("\n")[0]
     # No PAPI installation found, use default
     if papi_install_parent_directory is None:
         print("NO PAPI INSTALLATION SET")
         current_papi_default_dir_location="papi_builds"
         machine_type = platform.machine()
         if machine_type == "x86_64":
             name_of_papi_build = "papi_build_x86_gcc"
             papi_install_parent_directory = f"{current_papi_default_dir_location}/{name_of_papi_build}"
         elif machine_type == "aarch64":
             name_of_papi_build = "papi_build_aarch64_gcc"
             papi_install_parent_directory = f"{current_papi_default_dir_location}/{name_of_papi_build}"
         elif machine_type == "ppc64le":
             name_of_papi_build = "papi_build_ppc64le_gcc"
             papi_install_parent_directory = f"{current_papi_default_dir_location}/{name_of_papi_build}"

if papi_install_parent_directory is None:
    raise ModuleNotFoundError("A PAPI installation was not found. Set PAPI_DIR, see line for more details on installing cyPAPI.")

configure_extension_module(extension_module_papi, papi_install_parent_directory)

internal_compile_time_envs = {}
cuda_compiled_in_command = f"{papi_path}/bin/papi_component_avail | sed -n '/Compiled-in components:/,/Active components:/p' | grep 'Name:   cuda'"
# Check to see if the cuda component was compiled in
try:
    completed_process = subprocess.run(cuda_compiled_in_command, shell = True, check = True, capture_output = True)
# Cuda component was not compiled into PAPI
except subprocess.CalledProcessError:
    internal_compile_time_envs["CUDA_COMPILED_IN"] = False
# Cuda component was compiled into PAPI
else:
    internal_compile_time_envs["CUDA_COMPILED_IN"] = True

setup(
    name='cypapi',
    packages=['cypapi'],
    ext_modules = cythonize([extension_module_papi], compile_time_env = internal_compile_time_envs),
    install_requires = ['numpy'],
)
