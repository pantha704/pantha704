# probe — what survives GitHub's markdown sanitizer

## section one

<a name="anchor-name"></a>
<a id="anchor-id"></a>
<span id="anchor-span"></span>
<div id="anchor-div"></div>

### image map

<img src="assets/hero-light.svg" usemap="#m" width="200">
<map name="m"><area shape="rect" coords="0,0,100,50" href="#section-one" alt="x"></map>

### inline styles

<div style="color:red;display:flex">styled div</div>
<p style="color:red">styled p</p>
<table><tr><td style="background:#000;color:#fff">styled td</td></tr></table>

### details variants

<details><summary><a href="#section-one">summary link</a></summary>body text</details>

<details id="det-anchor"><summary>details with id</summary>inside details</details>

### misc

<kbd>Ctrl</kbd> <sub>sub</sub> <sup>sup</sup>

<div align="center">aligned div</div>
