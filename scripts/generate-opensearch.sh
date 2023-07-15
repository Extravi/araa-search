#!/bin/sh

if [ $DOMAIN ]; then
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<OpenSearchDescription xmlns=\"http://a9.com/-/spec/opensearch/1.1/\">
  <ShortName>TailsX</ShortName>
  <Url type=\"text/html\" template=\"$DOMAIN/search?q={searchTerms}\"/>
  <Url rel=\"suggestions\" type=\"application/x-suggestions+json\" method=\"get\" template=\"$DOMAIN/suggestions?q={searchTerms}\" />
  <OutputEncoding>UTF-8</OutputEncoding>
  <InputEncoding>UTF-8</InputEncoding>
  <Language>en-us</Language>
</OpenSearchDescription>" > ./static/opensearch.xml;
    rm static/opensearch.xml.example;
else
    echo "Make a DOMAIN env. variable & set it to your domain!
    (Ex; DOMAIN=https://www.yourdomain.com)";
    exit 1;
fi
