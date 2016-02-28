//=require jquery.min
//=require bootstrap/bootstrap.min
//=require select2/select2.min
//=require select2/select2_locale_ru

window.searchNow = (url) ->
    window.location.href = url+'?q='+$('.search-input').first().val()

window.Queue = {
    do: (key) ->
        if typeof window.Queue[key] != 'undefined'
            return window.Queue[key][0]() if typeof Queue[key][0] != 'undefined'
        return null
    add: (key, val) ->
        if typeof window.Queue[key] == 'undefined'
            window.Queue[key] = []
        return window.Queue[key].push val
}

getUrlVars = (win=window) ->
    vars = []
    hash = {}
    hashes = win.location.href.slice(win.location.href.indexOf('?') + 1).split('&')
    for i in hashes
        hash = i.split('=');
        if typeof hash[1] != 'undefined'
            vars[hash[0]] = hash[1].replace /%2F/g, '/'
    return vars

window.getUrlVars = getUrlVars

initPackage = (p, f) ->
    b = false
    for i in p
        b = true if window.location.pathname.indexOf(i) > -1
    f() if b

window.initPackage = initPackage

openDialogWindow = (obj, not_clean) ->
    o = $(obj)
    url = o.data 'url'
    $.get url, (d) ->
        m = $('#modal')
        c = m.find('.modal-content')
        c.html '' if not not_clean
        c.append d
        m.modal()

window.openDialogWindow = openDialogWindow

openDialogWindowSearch = (url, q) ->
    $.get url + '?q=' + $(q).val(), (d) ->
        m = $('#modal')
        c = m.find('.modal-content')
        c.html d
        m.modal()

window.openDialogWindowSearch = openDialogWindowSearch

class mField
    post: false
    name: ''
    errors_cont: ''
    constructor: (cont, @url, errors_cont) ->
        self = @
        @cont = $(cont)
        if not errors_cont?
            @errors_cont = $(@cont.attr('data-errors-cont'))
        else
            @errors_cont = $(errors_cont)
        @name = @cont.attr('name')
        return
    lets_post: (f) ->
        self = @
        d = {}
        d[self.name] = self.cont.val()
        $.post self.url, d, (data) ->
            self.clear()
            data = JSON.parse data
            if typeof data[self.name]['errors'] != 'undefined'
                for i in data[self.name]['errors']
                    self.addError i
            if typeof data[self.name]['messages'] != 'undefined'
                for i in data[self.name]['messages']
                    self.addMessage i
            f(data) if f?
            return
    addError: (text) ->
        @errors_cont.show().addClass('error').append(text).append $('<br>')
        return
    addMessage: (text) ->
        @errors_cont.show().addClass('success').append(text).append $('<br>')
        return
    clear: ->
        @errors_cont.removeClass('error').removeClass('success').hide().html ''
        return
    bind: ->
        self = @
        @post = true
        @cont.change ->
            self.clear()
            self.lets_post() if self.post

class mForm
    post: false
    constructor: (@fields, @url) -> return
    lets_post: (f) ->
        self = @
        d = {}
        for i in self.fields
            i.clear()
            d[i.name] = i.cont.val()
        $.post @url, d, (data) ->
            data = JSON.parse data
            for i of data
                a = data[i]
                if typeof a['errors'] != 'undefined'
                    for j in self.fields
                        if j.name == i
                            for m in a['errors']
                                j.addError m
                if typeof a['messages'] != 'undefined'
                    for j in self.fields
                        if j.name == i
                            for m in a['messages']
                                j.addMessage m
            f(data) if f?
            return
        return
    bind: ->
        self = @
        @post = true
        for i in @fields
            i.cont.change ->
                self.lets_post() if self.post

window.mField = mField
window.mForm = mForm

window.initPackage ['user/new', 'user/'+$('#id').val()+'/edit'], ->
    $('#lang').select2()
    $('#rank').select2()
    # $('#settings-tab a.active').tab 'show'

window.initPackage ['user/'+$('#id').val()+'/edit'], ->
    a = $('#lang')
    b = a.attr 'value'
    a.select2("val", b)

window.initPackage ['product/new', 'product/'+$('#id').val()+'/edit'], ->
    $('#category').select2()
    prev = ''
    setInterval ->
        v = window.getUrlVars document.getElementsByClassName('file-load')[0].contentWindow
        if typeof v.path != 'undefined'
            if v.path != prev
                $('#img-cont').removeClass 'hidden'
                $('#img-cont').attr 'src', '/media/cache/' + v.path.substr(0, v.path.lastIndexOf('.')) + '_400x400_85' + v.path.substr(v.path.lastIndexOf('.'))
                $('#img').val v.path
            prev = v.path
    , 500

window.initPackage ['product/'+$('#id').val()+'/edit'], ->
    a = $('#category')
    b = a.attr 'value'
    a.select2("val", b)

window.initPackage ['category/new', 'category/'+$('#id').val()+'/edit'], ->
    $('#parentid').change ->
        if parseInt(this.value) != 0
            $('#dcost').attr 'readonly', 'readonly'
            $('#paid').attr 'readonly', 'readonly'
        else
            $('#dcost').removeAttr 'readonly'
            $('#paid').removeAttr 'readonly'
    $('#parentid').change()

window.initPackage ['driver/map', 'driver/list'], ->
    window.MAP = null
    window.DRIVERS = []
    window.POSITION = null
    active_drivers = true
    map_loaded = false

    drawDriver = (coord, title) ->
        marker = new google.maps.Marker {
            position: new google.maps.LatLng parseFloat(coord.split(' ')[0]), parseFloat(coord.split(' ')[1])
            map: window.MAP
            title: title
        }
        window.DRIVERS.push marker
        return marker
    window.drawDriver = drawDriver


    drawDrivers = (silent=false) ->
        i.marker = window.drawDriver i.coord, i.name for i in window.fresh_drivers
        if not silent
            window.MAP.setZoom 12
            window.MAP.setCenter new google.maps.LatLng window.POSITION.coords.latitude, window.POSITION.coords.longitude
        return
    window.drawDrivers = drawDrivers


    removeDrivers = ->
        i.setMap null for i in window.DRIVERS
        window.DRIVERS = []
        return
    window.removeDrivers = removeDrivers


    success = (position) ->
        window.POSITION = position
        $('#map-cont').hide().removeClass('hidden').toggle()
        window.MAP = new google.maps.Map document.getElementById('map'), {
            zoom: 12
            center: new google.maps.LatLng position.coords.latitude, position.coords.longitude
        }
        drawDrivers()
        map_loaded = true
        window.Queue.do 'map'

    error = -> return


    load_map = ->
        if not map_loaded
            navigator.geolocation.getCurrentPosition success, error if navigator.geolocation
            window.setInterval ->
                window.refreshFreshDrivers() if active_drivers
            , 10000
            $('#load-map-button').remove()


    $('#load-map-button').click ->
        load_map()


    sad = $('#show_active_drivers')
    had = $('#hide_active_drivers')

    sad.click ->
        window.removeDrivers()
        sad.addClass 'hidden'
        had.removeClass 'hidden'
        active_drivers = true
        window.drawDrivers()

    had.click ->
        had.addClass 'hidden'
        sad.removeClass 'hidden'
        active_drivers = false
        window.removeDrivers()

    _showDriver_ = (url) ->
        $.get url, (data) ->
            active_drivers = false
            data = JSON.parse data
            window.removeDrivers()
            a = window.drawDriver data.coord, data.name
            window.MAP.setCenter a.position
            window.MAP.setZoom 16
            had.addClass 'hidden'
            sad.removeClass 'hidden'

    showDriver = (url) ->
        if not map_loaded
            load_map()
            window.Queue.add 'map', -> 
                _showDriver_(url)
        _showDriver_(url)
        return
    window.showDriver = showDriver

    refreshFreshDrivers = ->
        $.get window.fresh_drivers_url, (data) ->
            data = JSON.parse data
            window.fresh_drivers = data
            window.removeDrivers()
            window.drawDrivers true
    window.refreshFreshDrivers = refreshFreshDrivers
    return

window.initPackage ['driver/route'], ->
    window.POSITION = null
    window.MAP = null
    map_loaded = false
    window.YOUR_MARKER = null
    window.directionsService = new google.maps.DirectionsService()
    window.directionsDisplay = new google.maps.DirectionsRenderer();

    exportInformation = (r) ->
        $('#address-panel .for-marketplace').append r.routes[0].legs[0].end_address

    DrawRoute = ->
        if window.OrderNeedShop
            u = 0
            mLenght = 100000000
            mShop = null
            for i in window.OrderShops
                request = {
                    origin: new google.maps.LatLng window.POSITION.coords.latitude, window.POSITION.coords.longitude
                    destination: window.OrderAddress
                    waypoints: [
                        {
                            location: i.address
                            stopover: true
                        }
                    ]
                    travelMode: google.maps.TravelMode.DRIVING 
                }
                window.directionsService.route request, (r, s) ->
                    if s == google.maps.DirectionsStatus.OK
                        u++
                        d = 0
                        d += j.distance.value for j in r.routes[0].legs
                        if mLenght >= d
                            mLenght = d
                            mShop = r
                        if u == window.OrderShops.length
                            console.log mShop
                            window.directionsDisplay.setDirections mShop
                            exportInformation mShop

        else
            request = {
                origin: new google.maps.LatLng window.POSITION.coords.latitude, window.POSITION.coords.longitude
                destination: window.OrderAddress
                travelMode: google.maps.TravelMode.DRIVING
            }

            window.directionsService.route request, (r, s) ->
                window.directionsDisplay.setDirections r  if s == google.maps.DirectionsStatus.OK

    window.DrawRoute = DrawRoute

    success = (position) ->
        window.POSITION = position

        if not map_loaded
            map_loaded = true
            window.MAP = new google.maps.Map document.getElementById('map'), {
                zoom: 12
                center: new google.maps.LatLng position.coords.latitude, position.coords.longitude
            }
            window.directionsDisplay.setMap window.MAP
            window.DrawRoute()
        window.YOUR_MARKER.setMap null if window.YOUR_MARKER != null
        window.YOUR_MARKER = new google.maps.Marker {
            position: new google.maps.LatLng position.coords.latitude, position.coords.longitude
            map: window.MAP
            title: 'It\'s you.'
            icon: '/static/img/your_point.png'
        }
        

    error = -> return

    navigator.geolocation.watchPosition success, error if navigator.geolocation
    return

window.initPackage ['driver/route', 'driver/products'], ->
    ft = true
    success = (position) ->
        window.POSITION = position
        if ft
            ft = false
            sendDriverInfo()
        return
    error = -> return
    navigator.geolocation.watchPosition success, error if navigator.geolocation


    sendDriverInfo = ->
        data = {
            coord: window.POSITION.coords.latitude + ' ' + window.POSITION.coords.longitude
        }
        $.post '/driver/coord', data, (d) -> return

    setInterval ->
        try
            sendDriverInfo()
        catch e
    , 10000
    return

window.initPackage ['driver/orders'], ->
    ft = true
    success = (position) ->
        window.POSITION = position
        if ft
            ft = false
            sendDriverInfo()
        return
    error = -> return
    navigator.geolocation.watchPosition success, error if navigator.geolocation

    sendDriverInfo = ->
        data = {
            coord: window.POSITION.coords.latitude + ' ' + window.POSITION.coords.longitude
        }
        $.post '/driver/coord', data, (d) -> return

    sendDriverInfo2 = ->
        if $('#active-orders').hasClass('active')
            $('#tab-content').load '/driver/coord_get_orders?t=active&coord='+window.POSITION.coords.latitude+'+'+window.POSITION.coords.longitude+' #tab-content', () -> return
        else
            $('#tab-content').load '/driver/coord_get_orders?coord='+window.POSITION.coords.latitude+'+'+window.POSITION.coords.longitude+' #tab-content', () -> return

    setInterval ->
        try
            sendDriverInfo2()
        catch e
    , 10000
    return

window.initPackage ['order/list'], ->
    setInterval ->
        $('#list-table').load window.location.href+' #list-table', -> return
        return
    , 10000

window.initPackage ['order/calculation'], ->
    $('#driver_calc').select2()
    $('#driver_calc').select2('val', $('#driver_calc').attr 'value' )
    return

window.initPackage ['settings'], ->
    $('.switcher span').on 'click', ->
        $(this).parent().find('span').removeClass 'enabled'
        $(this).addClass 'enabled'
        $('.' + $(this).attr('d-param')).removeClass 'active'
        $('textarea[name=' + $(this).attr('d-param') + '_' + $(this).attr('d-lang') + ']').addClass 'active'
        return
    setInterval ->
        v = window.getUrlVars document.getElementsByClassName('file-load-logo')[0].contentWindow
        if typeof v.path != 'undefined'
            if String(prev) != String(v.path)
                document.getElementById('logoform').src="/admin/upload/logo?nocache="+nocache()
                $('#img-cont-logo').attr 'src', '/static/market/image/logo.png?nocache='+nocache()
            prev = v.path
        v = window.getUrlVars document.getElementsByClassName('file-load-about')[0].contentWindow
        if typeof v.path != 'undefined'
            if String(prev) != String(v.path)
                document.getElementById('aboutform').src="/admin/upload/about?nocache="+nocache()
                $('#img-cont-about').attr 'src', '/static/market/image/about-us/'+v.path+'?nocache='+nocache()
            prev = v.path
    , 500

nocache = ->
    return Math.random().toString(36).substring(7);

invert = (rgb) ->
  rgb = Array.prototype.join.call(arguments).match(/(-?[0-9\.]+)/g);
  for i in rgb.length
    rgb[i] = ((i == 3) ? 1 : 255) - rgb[i];
  return rgb;
