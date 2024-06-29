import abc
import dataclasses
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional


@dataclasses.dataclass
class BaseLauncher:
    """
    An "abstract" dataclass that describe how to start a software environment session.
    """

    # XXX: all fields defined MUST specify a default value (else inheritance issues)
    #   instead add them to the `required_fields` class variable.

    environ: Dict[str, str] = dataclasses.field(default_factory=dict)
    """
    Mapping of environment variables to set when starting the environment.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    command: List[str] = dataclasses.field(default_factory=list)
    """
    Arbitrary list of command line arguments to call at the end of the launcher execution.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    cwd: Optional[str] = None
    """
    Current working directory.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    required_fields: ClassVar[List[str]] = []
    """
    List of dataclass field that are required to have a non-None value when instancing.
    
    Note that your subclass must have the default field value set to None for this to work.
    
    Example::
    
          @dataclasses.dataclass
          class DemoLauncher(BaseLauncher):
              # override the BaseLauncher.environ field to make it required
              environ: Dict[str, str] = None
        
              required_fields = ["environ"]
    
    """

    name: ClassVar[str] = ".base"
    """
    A unique name among all subclasses.
    """

    def __post_init__(self):
        for field in dataclasses.fields(self):
            if field.name in self.required_fields and getattr(self, field.name) is None:
                raise ValueError(
                    f"Missing required field '{field.name}' for instance {self}"
                )

    @abc.abstractmethod
    def execute(self, tmpdir: Path, command: Optional[List[str]] = None) -> int:
        """
        Start the given environment and execute this python session.

        Optionally execute the given command in the environment.

        Args:
            tmpdir: filesystem path to an existing temporary directory
            command: optional list of command line arguments

        Returns:
            The exit code of the execution. 0 if successfull, else imply failure.
        """
        pass  # pragma: no cover

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the instance to a python dict object.
        """
        as_dict = dataclasses.asdict(self)
        # remove optional keys that don't have a value
        as_dict = {
            key: value
            for key, value in as_dict.items()
            if key or key in self.required_fields
        }
        return as_dict

    @classmethod
    def from_dict(cls, src_dict: Dict[str, Any]) -> "BaseLauncher":
        """
        Generate an instance from a python dict object with a specific structure.
        """
        return cls(**src_dict)
