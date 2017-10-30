import ConfigParser

configurationOptions =(
    ( 'logFile',        'logging',  'file',      'ums.log' ),
    ( 'logFormat',      'logging',  'format',    "%(asctime)-15s %(levelname)-8s %(filename)20s:%(lineno)-3d %(message)s" ),
    ( 'logDateFormat',  'logging',  'datefmt',   None ),
    ( 'logLevel',       'logging',  'level',     'INFO' ),
    ( 'logOverwrite',   'logging',  'overwrite', 1 )
)
configuration = {}
cmdline_args = None


def set_cmdline_args(args):
    global cmdline_args
    cmdline_args = vars(args)


def parseFile(filename):
    config_parser = ConfigParser.RawConfigParser()
    config_parser.readfp(open(filename))

    for option in configurationOptions:
        if config_parser.has_option(option[1], option[2]):
            configuration[option[0]] = config_parser.get(option[1], option[2])
        else:
            configuration[option[0]] = option[3]


def getOption(option):
    return configuration[option]


def getArg(arg):
    global cmdline_args
    return cmdline_args[arg]