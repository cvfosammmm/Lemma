# Lemma

Note-taking app for the GNU/Linux desktop, written in Python with Gtk.

**Warning: this app is currently in alpha stage, data loss is likely at this point. Please be careful and make regular backups.**

Website: <a href="https://www.cvfosammmm.org/lemma/">https://www.cvfosammmm.org/lemma/</a>

<a href="https://flathub.org/apps/org.cvfosammmm.Lemma"><img src="https://dl.flathub.org/assets/badges/flathub-badge-en.png" width="150" height="50" alt="Download on Flathub"></a>

![Screenshot](https://github.com/cvfosammmm/Lemma/raw/master/data/screenshot.png)

## Running Lemma (Debian, probably Ubuntu and other Distributions)

I develop Lemma on Debian and that's what I tested it with. On Debian derivatives (like Ubuntu) it should probably work the same. On distributions other than Debian and Debian derivatives it should work more or less the same. If you want to run Lemma from source on another distribution and don't know how please open an issue here on GitHub. I will then try to provide instructions for your system.

1. Run the following command to install prerequisite Debian packages:<br />
`apt-get install meson python3-gi gir1.2-gtk-4.0 gir1.2-pango-1.0 gettext python3-cairo python3-gi-cairo gir1.2-adw-1 python3-xdg python3-markdown-it python3-html2text`

2. Download und Unpack Lemma from GitHub

3. cd to Lemma folder

4. Run meson: `meson builddir`<br />
Note: Some distributions may not include systemwide installations of Python modules which aren't installed from distribution packages. In this case, you want to install Lemma in your home directory with `meson builddir --prefix=~/.local`.

5. Install Lemma with: `ninja install -C builddir`<br />
Or run it locally: `./scripts/lemma.dev`

## Getting in touch

Lemma development / discussion takes place on GitHub at [https://github.com/cvfosammmm/Lemma](https://github.com/cvfosammmm/Lemma "project url").

## License

Lemma is licensed under GPL version 3 or later. See the COPYING file for details.

NewComputerModern fonts are licensed under GustFLv1 or later (see [https://ctan.org/tex-archive/fonts/newcomputermodern](https://ctan.org/tex-archive/fonts/newcomputermodern)).

python_freetype (in the `lib` folder) is dual-licensed under the FreeType licence ([http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/docs/FTL.TXT](http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/docs/FTL.TXT)) and GPL version 2 or later ([http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/docs/GPLv2.TXT](http://git.savannah.gnu.org/cgit/freetype/freetype2.git/tree/docs/GPLv2.TXT)), to be compatible with FreeType itself.

Python_fontconfig and HarfPy (in the `lib` folder) are licensed under LGPL version 2.1 or later (see the COPYING files in their respective folders, under `lib`).
