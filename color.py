def is_primary(color: tuple[int, ...]) -> bool:
    color = color[:3]
    return color.count(256) == 1 and color.count(0) == 2

def is_secondary(color: tuple[int, ...]) -> bool:
    color = color[:3]
    return color.count(256) == 2 and color.count(0) == 1

def main() -> None:
    # Use Walrus operator to get next input until user enters 'q' and assign it to `response`.
    # Benefit of this is that if the input is empty, the loop will not continue.
    while response := input("Enter a color as three integers separated by spaces: "):
        
        # Use a match statement to decompose the input on a space
        match response.split():
            
            # Match the case of 3 integers separated by spaces                
            case [r, g, b, *a]:
                a = a[0] if a else '256'
                
                if not all(map(str.isdigit, [r, g, b, a])):
                    print(' ' * 50, end='\r')
                    print("Invalid input.", end='\r')
                    continue
                
                # Convert the input to integers and assign it to `color`
                color: tuple[int, int, int] = tuple(map(int, [r, g, b, a]))
                print(' ' * 50, end='\r') # this clears the previous line
                print(
                    f"RGB{color} is a Primary color."*is_primary(color) +
                    f"RGB{color} is a Secondary color"*is_secondary(color) +
                    f"RGB{color} is neither a Primary nor a Secondary color."*(not is_primary(color) and not is_secondary(color)) +
                    '\n'
                )
            
            # Match the case of a single 'q'
            case ['q']:
                print(' ' * 50, end='\r')
                print("Goodbye!", end='\r')
                break
            
            # Match the case of any other input
            case _:
                print(' ' * 50, end='\r')
                print("Invalid input.", end='\r')

if __name__ == "__main__":
    main()