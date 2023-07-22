def is_stable_statement(statement: str) -> bool:
    statement = statement.lower().replace("\r\n", "\\r\\n").replace("\n", "\\n").replace("\r", "\\r")

    return statement.find(" limit ") == -1 and statement.find("\\nlimit\\n") == -1 \
        and statement.find(" limit\\n") == -1 and statement.find("\\nlimit") == -1
