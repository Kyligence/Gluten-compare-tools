def is_stable_statement(statement: str) -> bool:
    statement = statement.lower().replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    return statement.find(" limit ") == -1
