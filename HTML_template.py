from string import Template 


TEMPL_PAGE = Template("""<html lang="fi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="Suodatettu uutislista high.fi tarjoamasta JSON-syötteestä">
    <meta name="keywords" content="uutisia, otsikoita">
    <meta name="description" content="Suodatetut uutisotsikot">

    <script src="https://use.fontawesome.com/91d24689a3.js"></script>

    <title>Uutisotsikot</title>

    <style>
      ${style}
    </style>

  </head>
  <body>
    <section id="main">
      <a href="${link}">${linktitle}</a><br>${extraspace}

      ${content}
      <br>
      <hr><br>

      <span style="font-size: 12px; color: #EEEEEE;">
        Uutisl&auml;hde: <a style="font-size: 16px; color: #8DB2E5;" href="https://high.fi">high.fi</a>
      </span>

    </section>
  </body>
</html>
""") 