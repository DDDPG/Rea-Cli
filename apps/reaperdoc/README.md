# ReaperDoc

ReaperDoc is a personal compilation of the REAPER .RPP project file parameter mapping table. It aims to provide a comprehensive and interactive reference for understanding the structure and parameters of REAPER project files. You could visit github page of this repo for searching: [Online Demo](https://dddpg.github.io/ReaperDoc/)

## Features

- **Interactive Project Structure**: Visualize the hierarchy of a .RPP file.
- **Parameter Documentation**: Detailed explanations of various chunks and parameters.
- **Search & Filter**: Quickly find specific parameters or sections.

## Acknowledgements

Special thanks to the **ReaTeam** for their extensive documentation, which provided significant support for this project:
- [ReaTeam State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions)

## Contributing

This project is a work in progress. There are still some parameters whose specific meanings have not been fully documented or verified.

If you have knowledge about these missing parameters or find any errors, your help is greatly appreciated!
- **Issues**: Please submit an issue if you find a bug or have a question.
- **Pull Requests**: PRs are welcome to add missing documentation or improve the app.

## Reviewed parameter updates

The reference includes 16 corrected entries and 34 supplemental entries. Field notes distinguish REAPER 7.48/macOS API and save checks from structural evidence; unresolved meanings remain marked as unknown. Supporting source material and experimental records are kept locally and are not part of this repository.

The online demo uses the same definitions as the source. Pushes to `main` build and deploy through GitHub Pages.

Validation: `npm run check`, then `npm run build`.
