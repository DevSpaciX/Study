      $(document).ready(function () {
          var silder = $(".owl-carousel");
          silder.owlCarousel({
              items: 1,
              center: false,
              nav: true,
              margin: 30,
              dots: false,
              loop: true,
              autoplay: true,
              autoPlaySpeed: 5000,
              autoPlayTimeout: 5000,
              autoplayHoverPause: true,
              navText: ["<i class='fa fa-arrow-left' aria-hidden='true'></i>", "<i class='fa fa-arrow-right' aria-hidden='true'></i>"],
              responsive: {
                  0: {
                      items: 1,
                  },
                  575: {items: 1},
                  768: {items: 2},
                  991: {items: 3},
              }
          });
      });