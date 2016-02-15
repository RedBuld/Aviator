/*common.js*/
function getURLVar(key) {
	var value = [];

	var query = String(document.location).split('?');

	if (query[1]) {
		var part = query[1].split('&');

		for (i = 0; i < part.length; i++) {
			var data = part[i].split('=');

			if (data[0] && data[1]) {
				value[data[0]] = data[1];
			}
		}

		if (value[key]) {
			return value[key];
		} else {
			return '';
		}
	}
}
$(window).resize(function(){
	xsmenu();
});
xsmenu = function(){
	if($('.menu').hasClass('fixed'))
	{
		$('.xsmenuover').css('height',$(window).height() - $('.hormenu').height() - 3);
	}else{
		$('.xsmenuover').css('height',$(window).height() - $('.header-container').height() + $(window).scrollTop());
	}
}
init_xs = function(){
	$('button.xs-menu').off('click').on('click',function(){
		if($('#xsmenu').hasClass('open')){
			$('#xsmenu').removeClass('open');
		}else{
			$('#xsmenu').addClass('open');
		}
	});
	$('#xsmenu p.plus').off('click').on('click',function(){
		console.log($(this).parent().hasClass('active'));
		if($(this).parent().hasClass('active'))
		{
			$(this).parent().removeClass('active');
			$(this).html('<i class="fa fa-plus"></i>');
		}else{
			$(this).parent().addClass('active');
			$(this).html('<i class="fa fa-minus"></i>');
		}
	});
}
$(document).ready(function() {
	init_xs();
	// Highlight any found errors
	$('.text-danger').each(function() {
		var element = $(this).parent().parent();
		
		if (element.hasClass('form-group')) {
			element.addClass('has-error');
		}
	});
	// Language
	$('#language a').on('click', function(e) {
		e.preventDefault();

		$('#language input[name=\'code\']').attr('value', $(this).attr('href'));

		$('#language').submit();
	});
	// Search
	$('#search input[name=\'search\']').parent().find('button').on('click', function() {
		url = $('base').attr('href') + 'search/';
		var value = $('#search input[name=\'search\']').val();
		if (value) {
			url += encodeURIComponent(value);
		}
		location = url;
	});
	$('#search input[name=\'search\']').on('keydown', function(e) {
		if (e.keyCode == 13) {
			$('#search input[name=\'search\']').parent().find('button').trigger('click');
		}
	});
	$('#search input[name=\'search\']').on('keyup',function(){
        searchq($(this).val());
    });
    $('#mapsmodal').on('shown.bs.modal', function(e) {
	    var element = $(e.relatedTarget);
	    console.log(element.data("lat"));
	    var data = element.data("lat").split(',')
	    initialize(new google.maps.LatLng(data[0], data[1]));
	    google.maps.event.trigger(map, 'resize');
	  });
});

/*cs.rb.js*/
/* SHARED VARS */
var touch = false;

// handles Animate
function dataAnimate(){
  $('[data-animate]').each(function(){
    
    var $toAnimateElement = $(this);
    
    var toAnimateDelay = $(this).attr('data-delay');
    
    var toAnimateDelayTime = 0;
    
    if( toAnimateDelay ) { toAnimateDelayTime = Number( toAnimateDelay ); } else { toAnimateDelayTime = 200; }
    
    if( !$toAnimateElement.hasClass('animated') ) {
      
      $toAnimateElement.addClass('not-animated');
      
      var elementAnimation = $toAnimateElement.attr('data-animate');
      
      $toAnimateElement.appear(function () {
        
        setTimeout(function() {
          $toAnimateElement.removeClass('not-animated').addClass( elementAnimation + ' animated');
        }, toAnimateDelayTime);
        
      },{accX: 0, accY: -80},'easeInCubic');
      
    }
    
  });
}
   
jQuery(document).ready(function($) {
  
  /* DETECT PLATFORM */
  $.support.touch = 'ontouchend' in document;
  
  if ($.support.touch) {
    touch = true;
    $('body').addClass('touch');
  }
  else{
	$('body').addClass('notouch');
  }
  // Product List
	$('#list-view').click(function() {
		$('#list-view').addClass('active');
		$('#grid-view').removeClass('active');
	});

	// Product Grid
	$('#grid-view').click(function() {
		$('#grid-view').addClass('active');
		$('#list-view').removeClass('active');
	});
  
	if (localStorage.getItem('display') == 'list') {
		$('#list-view').trigger('click');
	} else {
		$('#grid-view').trigger('click');
	}
  
  /* Handle Animate */
  if(touch == false){
    dataAnimate();
  }
  
	$(".open-panel,.close-panel").click(function(){
		$('body').toggleClass('openNav');
	});
	
	$(".icon-refine").click(function(){
		$('.category-list').toggleClass('openCate');
		$('.icon-refine').toggleClass('active');
	});
	
	
	$('.nav-pills li.parent > p').click(function(){

		if ($(this).text() == '+'){
			$(this).parent('li').children('.dropdown').slideDown(300);
			$(this).text('-');
		}else{
			$(this).parent('li').children('.dropdown').slideUp(300);
			$(this).text('+');
		}  
		
	});
	
});

// Js smartresize
(function($,sr){
  // debouncing function from John Hann
  // http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
  var debounce = function (func, threshold, execAsap) {
      var timeout;

      return function debounced () {
          var obj = this, args = arguments;
          function delayed () {
              if (!execAsap)
                  func.apply(obj, args);
              timeout = null; 
          };

          if (timeout)
              clearTimeout(timeout);
          else if (execAsap)
              func.apply(obj, args);

          timeout = setTimeout(delayed, threshold || 100); 
      };
  }
// smartresize 
 jQuery.fn[sr] = function(fn){  return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr); };

})(jQuery,'smartresize');

var TO = false;
$(window).smartresize(function(){
if(TO !== false)
    clearTimeout(TO);
 TO = setTimeout(resizeWidth, 400); //400 is time in miliseconds
});

function handleMenu(){
  // Listener for header
  var scrollTop = $(this).scrollTop();
  var heightHeader = $('#header').outerHeight();
  var heightNav = $('#rb_mainmenu').outerHeight();
  var heighttotal = (heightHeader+heightNav);
  
  if(getWidthBrowser() > 1024){
    if(scrollTop > heighttotal){
      if(!$('#rb_mainmenu').hasClass('show')){
        $('<div style="min-height:'+heightNav+'px"></div>').insertBefore('#rb_mainmenu');
        $('#rb_mainmenu').addClass('show').addClass('fadeInDown animated');
      }
    }else{
      if($('#rb_mainmenu').hasClass('show')){
        $('#rb_mainmenu').prev().remove();
        $('#rb_mainmenu').removeClass('show').removeClass('fadeInDown animated');
      }
    }
  }
};
$(window).load(function(){
	resizeWidth();
});

function resizeWidth(){
	var currentWidth = $(".rb-content-menu").outerWidth();	
	$('.mega-menu ul > li.parent > div').each(function(index, element) {		
		var menu = $('.rb-content-menu').offset();
		var dropdown = $(this).parent().offset();
		
		i = (dropdown.left + $(this).outerWidth()) - (menu.left + currentWidth);
		if (i > 0) {
			$(this).css('margin-left', '-' + (i+15)+ 'px');
		}
		else
			$(this).css('margin-left', '0px');
	});
}


$.fn.bttabs = function() {
	var selector = this;
	
	this.each(function() {
		var obj = $(this); 
		
		$(obj.attr('href')).hide();
		
		obj.click(function() {
			$(selector).removeClass('selected');
			
			$(this).addClass('selected');
			
			$($(this).attr('href')).fadeIn();
			
			var tabmodule = $(this).attr('data-crs');
			loadslider(tabmodule);
			
			$(selector).not(this).each(function(i, element) {
				$($(element).attr('href')).hide();
			});
			
			return false;
		});
	});

	$(this).show();
	
	$(this).first().click();
};

var btadd = {
	'cart': function(product_id) {
		$.ajax({
			url: '/add_product/'+product_id+'/1',
			type: 'get',
			dataType: 'json',
			success: function(json) {
				if (json['result']=='success') {
					addProductNotice(json['last']['name'], '<img src="'+json['last']['img']+'" alt="'+json['last']['name']+'" width="110px">', json['success'], 'success');
					$('#cart-total').html(json['cartheader']);
					$('#cart > ul').load('/cart_overview');
				}
			}
		});
	},
	'uncart': function(product_id) {
		$.ajax({
			url: '/remove_product/'+product_id,
			type: 'get',
			dataType: 'json',
			success: function(json) {
				if (json['result']=='success') {
					addProductNotice(json['last']['name'], '<img src="'+json['last']['img']+'" alt="'+json['last']['name']+'" width="110px">', json['success'], 'success');
					$('#cart-total').html(json['cartheader']);
					$('#cart > ul').load('/cart_overview');
				}
			}
		});
	},
	'remove': function(product_id) {
		$.ajax({
			url: '/delete_product/'+product_id,
			type: 'get',
			dataType: 'json',
			success: function(json) {
				if (json['result']=='success') {
					addProductNotice(json['last']['name'], '<img src="'+json['last']['img']+'" alt="'+json['last']['name']+'" width="110px">', json['success'], 'success');
					$('#cart-total').html(json['cartheader']);
					$('#cart > ul').load('/cart_overview');
				}
			}
		});
	}	
};

function getModalContent(product_id){	
        $('.rb-comb.rb-menu-fixed').css('padding-right','17px');
        $.ajax({
          url: '/quickview/' + product_id,
          dataType: 'html',
          beforeSend: function() {			
            $('.loading').html('<span class="wait">&nbsp;<img src="/static/market/image/loading.gif" alt="" /></span>');
            $('#myModal').html('');
          },		
          complete: function() {
            $('.wait').remove();
          },
          success: function(html) {
            $('#myModal').html(html);
            $('#myModal > .modal-dialog').css({
              'width': '95%',
              'max-width': '900px',
            });
          }
        });
      }

function addProductNotice(title, thumb, text, type) {
	$.jGrowl.defaults.closer = false;
	var tpl = thumb + '<h3>'+text+'</h3>';
	$.jGrowl(tpl, {		
		life: 1000,
		header: title,
		speed: 'medium'
	});
}

$.fn.addEr = function(text) {
	var di;
	di = $('<div></div>').addClass('er-er').addClass('alert').addClass('alert-danger').append(text);
	$(this).after(di);
};

Btn = (function() {
function Btn(tag, text, aclass, close) {
  var a;
  if (close == null) {
    close = false;
  }
  this.str = '';
  a = '';
  this.id = randId();
  if (aclass === '') {
    aclass = 'btn-default';
  }
  if (close) {
    a = ' data-dismiss="modal" aria-hidden="true"';
  }
  if (tag === 'a') {
    this.str = '<a href="#" id="' + this.id + '" class="btn ' + aclass + '"' + a + '>' + text + '</a>';
  } else {
    this.str = '<button type="button" id="' + this.id + '" class="btn ' + aclass + '"' + a + '>' + text + '</button>';
  }
  return this;
}

Btn.prototype.getHtml = function() {
  return this.str;
};

Btn.prototype.setOnclick = function(fun) {
  return $('#' + this.id).click(function() {
    fun.call();
  });
};

return Btn;

})();

Modal = (function() {

function Modal(title, html, btn, adelete, pause, callback) {
  var i, _i, _len;
  if (adelete == null) {
    adelete = true;
  }
  if (pause == null) {
    pause = 200;
  }
  if (callback == null) {
    callback = function() {};
  }
  this.callback = callback;
  this["delete"] = adelete;
  this.title = title;
  this.html = html;
  this.pause = pause;
  this.id = '';
  this.btn = '';
  for (_i = 0, _len = btn.length; _i < _len; _i++) {
    i = btn[_i];
    this.btn += i.getHtml();
  }
  return;
}

Modal.prototype.create = function() {
  var m, mbody, mc, md, mfooter, mhead, self;
  this.id = randId();
  mfooter = $('<div></div>').addClass('modal-footer');
  $(mfooter).append(this.btn);
  mbody = $('<div></div>').addClass('modal-body');
  $(mbody).append(this.html);
  mhead = $('<div></div>').addClass('modal-header');
  $(mhead).append('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h3>' + this.title + '</h3>');
  m = $('<div></div>', {
    id: this.id
  }).addClass('modal fade');
  md = $('<div></div>').addClass('modal-dialog');
  mc = $('<div></div>').addClass('modal-content');
  mc.append(mhead);
  mc.append(mbody);
  mc.append(mfooter);
  md.append(mc);
  m.append(md);
  $('body').append(m);
  if (this["delete"]) {
    self = this;
    $('#' + this.id).on('hide.bs.modal', function() {
      self.callback.call();
      setTimeout(function() {
        $('#' + self.id).remove();
        $('.modal-backdrop').animate({
          opacity: 0
        }, 100, function() {
          $(this).remove();
        });
        $('body').removeClass('modal-open');
      }, self.pause);
    });
  }
};

Modal.prototype.show = function() {
  $('#' + this.id).modal('show');
};

Modal.prototype.remove = function() {
  $('#' + this.id).modal('hide');
  $('#' + this.id).remove();
};

return Modal;

})();

$.fn.exists = function() {
return this.length > 0;
};

randId = function() {
var num;
while (true) {
  num = (Math.random() * 1000).toString().replace('.', '_');
  if (!$('#id_' + num).exists()) {
    return 'id_' + num;
  }
}
};
function email_subscribe(){
  $.ajax({
      url: '/subscribe',
      type: 'post',
      dataType: 'json',
      data:$("#subscribe").serialize(),
      beforeSend: function() {
        $('.success, .warning').remove();
      },    
      success: function(json) {
        if (json['error']) {
          $('#subscribe_result').html('<span class="error">' + json['error'] + '</span>');
        }
        if (json['success']) {          
          $('#subscribe')[0].reset();
          $('#subscribe_result').html('<span class="success">' + json['success'] + '</span>');
        }
      }     
  }); 
}
function email_unsubscribe(){
  $.ajax({
      url: '/unsubscribe',
      type: 'post',
      dataType: 'json',
      data:$("#subscribe").serialize(),
      beforeSend: function() {
      	$('.success, .warning').remove();
      },    
      success: function(json) {
        if (json['error']) {
          $('#subscribe_result').html('<span class="error">' + json['error'] + '</span>');
        }
        if (json['success']) {
          $('#subscribe')[0].reset();
          $('#subscribe_result').html('<span class="success">' + json['success'] + '</span>');
        }
      } 
  }); 
}

/*FAQ*/
$(document).ready(function(){
	$('.item-title').click(function(){
		$('.item-content').slideUp();
		$('.icon-toggle').removeClass('close').addClass('open');
		$('.item').removeClass('active');
		if($(this).next().is(":visible"))
		{
			$(this).find('.icon-toggle').removeClass('close').addClass('open');
			$(this).next().slideUp();
			$(this).parent().removeClass('active');
		}
		else
		{
			$(this).find('.icon-toggle').removeClass('open').addClass('close');
			$(this).next().slideDown();
			$(this).parent().addClass('active');
		}
	})
});

/*tabs.js*/
$.fn.bttabs = function($show_slider) {
	var selector = this;
	
	this.each(function() {
		var obj = $(this); 
		
		$(obj.attr('href')).hide();
		
		obj.click(function() {
			$(selector).removeClass('selected');
			
			$(this).addClass('selected');
			
			$($(this).attr('href')).fadeIn();
			
			var tabmodule = $(this).attr('data-crs');
			
			if($show_slider){
				loadslider(tabmodule);
			}
			
			$(selector).not(this).each(function(i, element) {
				$($(element).attr('href')).hide();
			});
			
			return false;
		});
	});

	$(this).show();
	
	$(this).first().click();
};
/**/
function searchq(string){
	if(string!='')
	{
		$.ajax({
	        url: '/search/'+string,
	        type: 'post',
	        dataType: 'json',
	        success: function (data) {
	        	if( !($.isEmptyObject(data['products'])) ) {
	        		$('#search_results').html('');
	        		products = data['products']; t = 0;
		        	for (var i in products) {
		        		if(t<5){
		        			t++;
		        			$('#search_results').append('<li data-value="'+i+'"><div class="image"><a href="/product/'+i+'"><img src="'+products[i]['img']+'"></a></div><div class="info"><div class="name"><a href="/product/'+i+'">'+products[i]['name']+'</a></div><div class="price">'+products[i]['price']+'</div></div></li>');
		        		}
		        	}
		        	if(data['counts']['val'] > 5){
		        		$('#search_results').append('<a href="/search/'+string+'" class="showmemore">'+data['counts']['text']+'</a>');
		        	}
		        	$('#search_results').show();
		        }else{
		        	$('#search_results').hide();
		        }
	        }
		});
	}else{
    	$('#search_results').hide();
    }
}
/*share.js*/
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
/*gmaps*/
var map;
function initialize(myCenter) {
	var marker = new google.maps.Marker({
        position: myCenter
    });
	var mapProp = {
        center: myCenter,
        zoom: 17,
        disableDefaultUI: true,
        streetViewControl: true,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), mapProp);
    marker.setMap(map);
};