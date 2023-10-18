from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 

spec = spec_from_loader("config_file_example", SourceFileLoader("config_file_example", "config_file_example.txt"))
bot_config_data = module_from_spec(spec)
spec.loader.exec_module(bot_config_data)
