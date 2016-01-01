Share = {
  vkontakte: function(purl, ptitle, pimg, text) {
    url  = 'http://vkontakte.ru/share.php?';
    url += 'url='          + encodeURIComponent(purl);
    url += '&title='       + encodeURIComponent(ptitle);
    url += '&description=' + encodeURIComponent(text);
    url += '&image='       + encodeURIComponent(pimg);
    url += '&noparse=true';
    Share.popup(url);
  },
  facebook: function(purl, ptitle, pimg, text) {
    url  = 'http://www.facebook.com/sharer.php?s=100';
    url += '&p[title]='     + encodeURIComponent(ptitle);
    url += '&p[summary]='   + encodeURIComponent(text);
    url += '&p[url]='       + encodeURIComponent(purl);
    url += '&p[images][0]=' + encodeURIComponent(pimg);
    Share.popup(url);
  },
  odnoklassniki: function(purl, text) {
    url  = 'http://www.odnoklassniki.ru/dk?st.cmd=addShare&st.s=1';
    url += '&st.comments=' + encodeURIComponent(text);
    url += '&st._surl='    + encodeURIComponent(purl);
    Share.popup(url);
  },
  twitter: function(purl, ptitle) {
    url  = 'http://twitter.com/share?';
    url += 'text='      + encodeURIComponent(ptitle);
    url += '&url='      + encodeURIComponent(purl);
    url += '&counturl=' + encodeURIComponent(purl);
    Share.popup(url);
  },
  popup: function(url) {
    window.open(url,'','toolbar=0,status=0,width=626,height=436');
  }
};
$(document).ready(function(){
  var s = 0; var sid = 0; var share_show;
  $('.shorty')
  .mouseenter(function() {
    clearTimeout(share_show);
    sid = $(this).attr('data-id');
    if(!s){$('.d-'+sid).toggle()} s = 1;
  })
  .mouseleave(function() {
    share_show = setTimeout(function(){
      $('.d-'+sid).toggle(); s = 0;
    },100);
    $('.d-'+sid).mouseenter(function(){
      clearTimeout(share_show);
       s = 1;
    })
    .mouseleave(function() {
      clearTimeout(share_show);
      share_show = setTimeout(function(){
        $('.d-'+sid).toggle(); s = 0;
      },100);
    });
  });
});