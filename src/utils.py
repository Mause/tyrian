if 'logger' not in globals():
    import logging

    logger = logging.getLogger('Main')
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    if not logger.handlers:
        hdlr = logging.StreamHandler()
        hdlr.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            # '%(asctime)s - '
            '%(name)s - '
            '%(levelname)s '
            '%(filename)s:%(lineno)d: '
            '%(message)s')
        hdlr.setFormatter(formatter)

        logger.addHandler(hdlr)


