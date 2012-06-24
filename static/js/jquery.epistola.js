// vim: set ts=4 sw=4 sts=4 et ai:

(function($) {

    var methods = {
        show : function( options ) {
            var defaults = {
                rel: null,
                data: null,
                use_xhr: false,
                url: null,
                name: 'XXX Add a name attribute to the overlay initiating element',
                dataComplete: null 
            }

            var opts =  $.extend(defaults, options);

            return this.each(function() {
                // grab the overlay we want to work with using the rel attribute
                var overlayObject;
                if (!opts.rel)
                    overlayObject = $('#overlay_top_div'); // default overlay defined in template
                else
                    overlayObject = $(opts.rel); // Supplied overlay in that case

                var overlayContent = overlayObject.find('.overlay_content');

            
                // Function that checks if a form exists in the overlayContent. If it does
                // we will set the action attribute to the supplied url.

                function checkForForm() {
                    var form = overlayContent.find('form');
                    if (form.length > 0)
                        form.attr('action', opts.url)
                }


                // If we use xhr it means we want to do a ajax call. We use the url
                // given in the href of the element and we append the data to the
                // content, if we dont use xhr we use the supplied data (if any).
                if (opts.use_xhr) {
                    var xhrObj = $.get(opts.url, function(data, status, xhr) {
                            overlayContent.append(data);
                            checkForForm();
                        }, 'html'
                    );
                    xhrObj.done(function() {
                        if (opts.dataComplete)
                            opts.dataComplete();
                    });
                }
                else { 
                    // Append the supplied data to the content 
                    overlayContent.append(opts.data);
                    checkForForm();
                    if (opts.dataComplete)
                        opts.dataComplete();

                }
                
                // Set the overlay title
                overlayObject.find('.overlay_title').html(opts.name);

                overlayObject.data('overlay', $(this));

                // Attach the overlay to the body so it can be positioned relative 
                // to the body instead of some position:relative div
                overlayObject.appendTo('body');
                
                scrollTop = $(window).scrollTop();
                $('#page_content').css({
                    position: 'fixed',
                    top: -scrollTop
                });
                $(window).scrollTop(0);
                overlayObject.show();

                overlayObject.find('.overlay_close').click(function(e) {
                    $(this).baseOverlay('hide', true, true, overlayObject, overlayContent);
                    e.preventDefault();
                });
            }); 
        },
        hide : function(force, removeChildren, overlay, overlayContent) {
            return this.each(function() {
                /* 
                 * Hides overlay's and resets the position of #container. 
                 * @param force: force a hide
                 * @param removeChildren: Boolean of child elements needs to be removed
                 * @param overlay: the overlay div that needs to be hidden
                 * @param overlayContent: the content inside the overlay
                 */
                if (!overlay.is(':visible'))
                    return;

                // don't close when there's input and we're not forcing
                if (!force) { return; }
               
                // get the offset so we can reset the scollposition 
                var scrollPosition = $('#page_content').offset().top;
                
                if (removeChildren)
                    overlayContent.empty();

                overlay.hide();
                // show underlay overflow
                $('#page_content').css({
                    position: 'relative',
                    top: 'auto'
                });

                // Set the scrollposition back 
                $(window).scrollTop(-scrollPosition);
            });
        },
    };

    $.fn.extend({
        baseOverlay: function(method) {
            // Method calling logic
            if (methods[method]) {
                // apply calls a function with a set of arguments, Array.prototype.slice.call will
                // return all elements of the array starting from index 1 (removing the method argument)
                return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
            }
            // When no method is supplied we use the default, in this case the show function.
            else if (typeof method === 'object' || ! method)
                return methods.show.apply(this, arguments);
            else
                $.error( 'Method ' +  method + ' does not exist on jQuery.epistola' );
        }  
    });
})( jQuery );
