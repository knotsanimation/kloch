import dataclasses
import logging
import sys
from typing import Any
from typing import Callable
from typing import Optional

import rez.resolved_context
import rez.package_filter
import rez.package_order
import rez.solver
import rez.packages

from ._base import enforce_callback_type
from ._base import enforce_int_type
from ._base import enforce_list_path_type
from ._base import serialize_callback
from ._base import PackageManagerProfileBase


LOGGER = logging.getLogger(__name__)


RezCallbackType = Callable[
    [rez.solver.SolverState], tuple[rez.solver.SolverCallbackReturn, str]
]
RezPackageLoadCallbackType = Callable[[rez.packages.Package], None]

REZ_CONFIG_PACKAGE_PATHS_TOKEN = "%PACKAGE_PATHS%"


@dataclasses.dataclass
class RezEnvironmentProfile(PackageManagerProfileBase):
    """
    A datastructure that allow to create a rez environment.
    """

    requires: list[str]
    verbosity: int = 0
    caching: Optional[bool] = None
    package_paths: Optional[list[str]] = None
    package_filter: Optional[rez.package_filter.PackageFilterList] = None
    package_orderers: Optional[rez.package_order.PackageOrderList] = None
    max_fails: int = -1
    add_implicit_packages: bool = True
    time_limit: int = -1
    callback: Optional[RezCallbackType] = None
    package_load_callback: Optional[RezPackageLoadCallbackType] = None
    suppress_passive: bool = False
    print_stats: bool = False
    package_caching: Optional[bool] = None

    def execute(self, command=None):
        from rez.config import config

        context = self.get_resolved_context()

        if not context.status == rez.resolved_context.ResolverStatus.solved:
            context.print_info(buf=sys.stderr)
            return -1

        LOGGER.debug("executing interactive shell")
        returncode, _, _ = context.execute_shell(
            shell=config.default_shell,
            command=command,
            block=True,
            quiet=False,
        )
        return returncode

    def get_resolved_context(self):
        # deferred import
        from rez.config import config

        package_paths = self.package_paths

        # XXX: mechanism to allow an "append" to the original package_paths
        #   defined in the rez config
        if package_paths and REZ_CONFIG_PACKAGE_PATHS_TOKEN in package_paths:
            index = package_paths.index(REZ_CONFIG_PACKAGE_PATHS_TOKEN)
            package_paths.pop(index)
            package_paths.insert(index, config.packages_path)

        context = rez.resolved_context.ResolvedContext(
            package_requests=self.requires,
            verbosity=self.verbosity,
            caching=self.caching,
            package_paths=package_paths,
            package_filter=self.package_filter,
            package_orderers=self.package_orderers,
            max_fails=self.max_fails,
            add_implicit_packages=self.add_implicit_packages,
            time_limit=self.time_limit,
            callback=self.callback,
            package_load_callback=self.package_load_callback,
            suppress_passive=self.suppress_passive,
            print_stats=self.print_stats,
            package_caching=self.package_caching,
        )
        return context

    def to_dict(self) -> dict:
        params_dict = {
            "verbosity": self.verbosity,
            "max_fails": self.max_fails,
            "add_implicit_packages": self.add_implicit_packages,
            "time_limit": self.time_limit,
            "suppress_passive": self.suppress_passive,
            "print_stats": self.print_stats,
        }

        if self.caching is not None:
            params_dict["caching"] = self.caching

        if self.package_paths is not None:
            params_dict["package_paths"] = self.package_paths

        if self.package_filter is not None:
            params_dict["package_filter"] = self.package_filter.to_pod()

        if self.package_orderers is not None:
            params_dict["package_orderers"] = self.package_orderers.to_pod()

        if self.callback is not None:
            params_dict["callback"] = serialize_callback(self.callback)

        if self.package_load_callback is not None:
            params_dict["package_load_callback"] = serialize_callback(
                self.package_load_callback
            )

        if self.package_caching is not None:
            params_dict["package_caching"] = self.package_caching

        return {
            "params": params_dict,
            "requires": self.requires,
        }

    @classmethod
    def name(cls):
        return "rezenv"

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "RezEnvironmentProfile":
        rezroot = src_dict

        params = rezroot.get("params", {})
        package_requests = rezroot["requires"]

        package_paths: list[str] = params.get("package_paths")
        if package_paths:
            package_paths = enforce_list_path_type(
                package_paths,
                excludes=[REZ_CONFIG_PACKAGE_PATHS_TOKEN],
            )

        verbosity = params.get("verbosity", 0)
        verbosity = enforce_int_type(verbosity)

        caching = params.get("caching", None)

        package_filter = params.get("package_filter", None)
        if package_filter:
            package_filter = rez.package_filter.PackageFilterList.from_pod(
                package_filter
            )

        package_orderers = params.get("package_orderers", None)
        if package_orderers:
            package_orderers = rez.package_order.PackageOrderList.from_pod(
                package_orderers
            )

        max_fails = params.get("max_fails", -1)
        max_fails = enforce_int_type(max_fails)

        add_implicit_packages = params.get("add_implicit_packages", True)

        time_limit = params.get("time_limit", -1)
        time_limit = enforce_int_type(time_limit)

        callback = params.get("callback", None)
        if callback:
            callback = enforce_callback_type(callback)

        package_load_callback = params.get("package_load_callback", None)
        if package_load_callback:
            package_load_callback = enforce_callback_type(package_load_callback)

        suppress_passive = params.get("suppress_passive", False)
        print_stats = params.get("print_stats", False)
        package_caching = params.get("package_caching", None)

        return RezEnvironmentProfile(
            requires=package_requests,
            package_paths=package_paths,
            verbosity=verbosity,
            caching=caching,
            package_filter=package_filter,
            package_orderers=package_orderers,
            max_fails=max_fails,
            add_implicit_packages=add_implicit_packages,
            time_limit=time_limit,
            callback=callback,
            package_load_callback=package_load_callback,
            suppress_passive=suppress_passive,
            print_stats=print_stats,
            package_caching=package_caching,
        )
