import fs from 'node:fs';

const languages = ['de', 'es', 'fr', 'it', 'ja', 'ko', 'nl', 'pt-br', 'zh-cn'];
const pages = {
  'index.html': ['../index.html', 'Leap Journey'],
  'privacy.html': ['../privacy.html', 'Leap Journey Privacy Policy'],
  'support.html': ['../support.html', 'Leap Journey Support'],
  'terms.html': ['../terms.html', 'Leap Journey Terms of Use'],
};

for (const language of languages) {
  for (const [file, [target, title]] of Object.entries(pages)) {
    const canonical = `https://micahwalkerdesign.github.io/NurturaSite/${target.slice(3)}`;
    const html = `<!DOCTYPE html>
<html lang="${language}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="refresh" content="0; url=${target}" />
  <link rel="canonical" href="${canonical}" />
  <title>${title}</title>
</head>
<body>
  <p>The current ${title} is available in English at <a href="${target}">${target}</a>.</p>
</body>
</html>
`;
    fs.writeFileSync(`${language}/${file}`, html);
  }
}
