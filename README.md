<!--
The pictures are built from the files in content/.

name and the lines under the name: content/profile.json
  name and bio. They are drawn into assets/profile/header-words.svg only.
account links under the portrait: content/profile.json, the links list
  label is the words beside the icon. url is where a click goes.
  Type the account there. The icon files in assets/profile/icons stay as they are.
  Facebook, GitHub, and LinkedIn are separate pictures, so a click opens url
  instead of opening the picture file.
one project per object, in order: content/projects.json
  image is a planet file already in assets/, or a new one
  imageSide is "left" or "right"
  badge is "PRIVATE" or ""
  description, detail, and tags are the words on the card
stack icons: drop an .svg or .png into assets/stacks, then rebuild.
  name them 01-something.svg, 02-something.svg to set the order
quotes, one per line: content/quotes.txt
  a credit after an em dash is kept in the file and left off the picture
usernames: content/stats.json
  github_username is already set
  leetcode_username and duolingo_username stay empty until you fill them
  with no Duolingo username, the lower number counts up by one each day

Pushing a change in content/ redraws the pictures on GitHub.
The picture address changes with the words, so the page does not keep the old drawing.
-->

<table cellspacing="0" cellpadding="0">
<tr>
<td width="37%" align="center" valign="top">
<img src="assets/profile/header-portrait.svg" alt="" width="100%">
<a href="https://facebook.com/your-account"><img align="absmiddle" src="assets/profile/icons/facebook.svg" width="32" height="32" alt="Facebook"><img align="absmiddle" src="assets/profile/icons/facebook-label.svg" height="32" alt="Facebook"></a><br>
<a href="https://github.com/alyyyyyanna"><img align="absmiddle" src="assets/profile/icons/github.svg" width="32" height="32" alt="GitHub"><img align="absmiddle" src="assets/profile/icons/github-label.svg" height="32" alt="Github"></a><br>
<a href="www.linkedin.com/in/alyanna-miñoza-30818a345"><img align="absmiddle" src="assets/profile/icons/linkedin.svg" width="32" height="32" alt="LinkedIn"><img align="absmiddle" src="assets/profile/icons/linkedin-label.svg" height="32" alt="LinkedIn"></a>
</td>
<td width="63%" valign="top">
<img src="assets/profile/header-words.svg" alt="Alyanna Marie Minoza. " width="100%">
</td>
</tr>
</table>

<br>

<p align="center">
  <img src="assets/profile/tagline.svg" alt="code that tells a story" width="100%">
</p>

<p align="center">
  <img src="assets/profile/stack-field.svg" alt="stack" width="100%">
</p>

<p align="center">
  <img src="assets/profile/projects-label.svg" alt="projects" width="100%">
</p>

<p align="center">
  <img src="assets/profile/cards/Olympus Mons.svg" alt="Olympus Mons" width="100%">
</p>
<p align="center">
  <img src="assets/profile/cards/grid9ora.svg" alt="grid9ora" width="100%">
</p>
<p align="center">
  <img src="assets/profile/cards/Space Traveler.svg" alt="Space Traveler" width="100%">
</p>

<table>
<tr>
<td width="58%" valign="top">
<img src="assets/profile/activity.svg?v=7d8e908a" alt="activity" width="100%">
</td>
<td width="42%" valign="top">
<img src="assets/profile/quote.svg?v=04ae86df" alt="A quote that changes every day" width="100%">
</td>
</tr>
</table>
