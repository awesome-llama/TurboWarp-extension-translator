

### Caveats

- Does not account for behaviour in recursion. Scratch does not maintain variable scope within each run of a custom block, the variables are shared across all calls. 
- There are some edge cases with differing behaviour. Some are due to Scratch being a bit difficult to work with (e.g. handling of NaN, casting to bools). 
- There isn't a full guarantee that the code is perfectly formatted and valid in project.json. You may want to try some... let's call it *block laundering*. Load the project in the editor and save it again. 