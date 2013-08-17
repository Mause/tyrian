var me = {name: 'Dominic'};

var maybe = function(){
    return Math.random() > 0.5;
};

var so = function(m) {
    return '' + this.name + ' will ' + (m() ? '' : 'not ') + 'call';
};


so.call(me, maybe);
