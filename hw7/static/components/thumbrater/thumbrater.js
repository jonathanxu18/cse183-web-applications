// Anonymous self-invoking function 
(function(){

    var thumbrater = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    // Setting the data propety of thumbrater variable
    thumbrater.data = function() {
        var data = {
            rating: 0,
            get_url: this.url,
            set_url: this.callback_url,
        };
        // When we call 'load', 'this' in 'load' will be data since call() is used
        thumbrater.methods.load.call(data);
        //console.log(data)
        return data;
    };

    thumbrater.methods.set_rating = function(rate) {
        this.rating = rate;
        axios.get(this.set_url, 
            {params: 
                {rating: this.rating}
            });
    };

    // Retrieving the ratings from 'url' and 'callback_url'
    thumbrater.methods.load = function() {

        let self = this;
        axios.get(self.get_url).then(function(result) {
            //console.log("rating: " + this.data)
            console.log(result.data.rating);

            // Set rating from database

            self.rating = result.data.rating;
            //console.log(thumbrater.data.rating)
        });
    };

    // Register component
    utils.register_vue_component('thumbrater', 'components/thumbrater/thumbrater.html',
        function(template) {

            // Setting template field for thumbrater
            thumbrater.template = template.data;
            return thumbrater;
        });
    
    

})();
