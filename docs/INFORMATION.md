# Info Command

Information commands can be used to fetch data quickly from a text file which is your database.
Lets say `i` is key command and you can find `info.diff` file in `/python/i/`, which can categorize in hierarchical structure.
`diff` extension is used because of simple folding style view in notepad++

## Notepad folding style
diff language to store information, as it appears to be easy to use the folding structure
Style and keywords can be checked here from notepad++ source code
https://github.com/notepad-plus-plus/notepad-plus-plus/blob/master/lexilla/lexers/LexDiff.cxx
There is no external language model file to define diff language syntax for notepad++
In short these keywords are used to form folding structure:
1. first level folding: `Index: `
2. second level folding:  `--- `
3. third level folding: `@ `

There are some existing example to use them right away:

Use `WinKey + r` to open run panel, and then type

- `i title1 topic1.2` => to see content under topic1.2
- `i title1` => to see subtopics under title1
- `i` => to see all top level topics
- `i -help` => to open `info.diff` file to edit

When reaching to the content, you can select a line, line content will be copied to clipboard, or it opens browser if the line is url address.
While the console is open, you can type `i` and `Enter` to open `info.diff` file in correct line.
You can also type `e` or `exit` and `Enter` to exit the console.
Even you use capital letter for topics or sub-topics in `info.diff`, all commands and switches to input to run panel should be lowercase.



![Alt text](/images/info_case_1.gif)
