FROM denoland/deno:ubuntu-1.37.2

RUN echo "nobody:x:1000:1000:::" > /etc/passwd
RUN echo "nobody::1000:nobody" > /etc/group

COPY monitoring /monitoring
COPY entries /entries
COPY entrypoint.sh /entrypoint.sh
RUN touch /flag.txt

RUN chown -R nobody:nobody /monitoring /entries /entrypoint.sh /flag.txt
RUN chmod -R 500 /entries
RUN chmod 500 /monitoring

USER nobody

ENTRYPOINT [ "sh", "/entrypoint.sh" ]
