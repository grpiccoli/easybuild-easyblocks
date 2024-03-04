from easybuild.easyblocks.generic.binary import Binary
from easybuild.framework.easyconfig.easyconfig import EasyConfig
from easybuild.tools.run import run_cmd
from distutils.version import LooseVersion
from easybuild.tools.build_log import EasyBuildError

class PackedBinaryVersionCheck(Binary):

    @staticmethod
    def __init__(self, *args, **kwargs):
        """Initializer for the EasyBlock."""
        super(PackedBinary, self).__init__(*args, **kwargs)

    def configure_step(self):
        """Check dependencies' versions against specified requirements."""
        if hasattr(self.cfg, 'dependencies') and self.cfg['dependencies']:
            dependencies = self.cfg['dependencies']
            for dep in dependencies:
                dep_name = dep['name']
                required_version = dep['version']  # This assumes exact version requirement; adapt as needed

                # Attempt to get the installed version of the dependency
                installed_version = get_software_version(dep_name)
                if not installed_version:
                    raise EasyBuildError(f"Failed to obtain version for dependency {dep_name}")

                # Check if the installed version satisfies the required version
                if not self._version_satisfies(installed_version, required_version):
                    raise EasyBuildError(f"Dependency {dep_name} version {installed_version} does not satisfy the requirement {required_version}")
                else:
                    dep['version'] = installed_version

        super(PackedBinary, self).configure_step()

    def _version_satisfies(self, installed_version, required_versions):
        """Check if the installed version satisfies the required version range."""
        required_versions_array = required_versions.split("|")

        for required_version in required_versions_array:
            # Split the range into parts (assuming AND logic for multiple conditions)
            range_parts = required_version.split(",")

            for part in range_parts:
                operator, version = part[:2], part[2:]
                # Convert versions to a format that can be compared
                installed_ver_tuple = self._version_to_tuple(installed_version)
                required_ver_tuple = self._version_to_tuple(version)

                if operator == ">=" and not (installed_ver_tuple >= required_ver_tuple):
                    return False
                elif operator == "==" or operator == "=" or operator == "" and not (installed_ver_tuple == required_ver_tuple):
                    return False
                elif operator == "<=" and not (installed_ver_tuple <= required_ver_tuple):
                    return False
                elif operator == ">" and not (installed_ver_tuple > required_ver_tuple):
                    return False
                elif operator == "<" and not (installed_ver_tuple < required_ver_tuple):
                    return False

        # If all conditions are met
        return True

    def _version_to_tuple(self, version_str):
        """Convert a version string like '2016a' to a comparable tuple."""
        # Split version into numeric and letter parts, e.g., '2016a' -> (2016, 'a')
        match = re.match(r"(\d+)([a-z]*)", version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")

        year, subversion = match.groups()
        # Convert year to int and treat subversion letter as a tuple for comparison
        return (int(year), subversion)

