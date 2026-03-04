from Core.Rafael import Rafael

rafael = Rafael()

if __name__ == "__main__":
    while True:
        user_input = input("Tú: ")
        print("Rafael:", rafael.ask_rafael(user_input))