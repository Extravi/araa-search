#!/bin/sh
# Generates the opensearch.xml file based off of a $DOMAIN env. var.
# Fails if $DOMAIN is blank or not set.

if [ $DOMAIN ]; then
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<OpenSearchDescription xmlns=\"http://a9.com/-/spec/opensearch/1.1/\">
  <ShortName>Araa</ShortName>
  <Url type=\"text/html\" template=\"https://$DOMAIN/search?q={searchTerms}\"/>
  <Url rel=\"suggestions\" type=\"application/x-suggestions+json\" method=\"get\" template=\"https://$DOMAIN/suggestions?q={searchTerms}\" />
  <OutputEncoding>UTF-8</OutputEncoding>
  <InputEncoding>UTF-8</InputEncoding>
  <Language>en-us</Language>
</OpenSearchDescription>" > ./static/opensearch.xml;
else
    echo "Make a DOMAIN env. variable & set it to your domain!
    (Ex; DOMAIN=www.yourdomain.com)";
    exit 1;
fi
