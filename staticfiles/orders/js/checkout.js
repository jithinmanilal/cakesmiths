var fname = $("#fname").text();
var email = $("#email").text();
var phone = $("#phone").text();
var grand_total = $("#grand_total").text();
var options = {
    "key": "rzp_test_fgZ1PQfYWRTKtv", // Enter the Key ID generated from the Dashboard
    "amount": grand_total, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    "currency": "INR",
    "name": "CakeSmiths", //your business name
    "description": "Thankyou",
    "image": "https://example.com/your_logo",
    "handler": function (response){
        alert(response.razorpay_payment_id);
        $.ajax({
            method: "POST",
            url: "/orders/payment",
            data: {
                "payment_method": "Razorpay",
                "payment_id" : response.razorpay_payment_id,
                csrfmiddlewaretoken: token
            },
            dataType: "dataType",
            success: function (response) {
                
            }
        });
    },
    "prefill": {
        "name": fname, //your customer's name
        "email": email,
        "contact": phone
    },
    "theme": {
        "color": "#3399cc"
    }
};
var rzp1 = new Razorpay(options);
rzp1.on('payment.failed', function (response){
        alert(response.error.code);
        alert(response.error.description);
        alert(response.error.source);
        alert(response.error.step);
        alert(response.error.reason);
        alert(response.error.metadata.order_id);
        alert(response.error.metadata.payment_id);
});
document.getElementById('rzpbutton').onclick = function(e){
    rzp1.open();
    e.preventDefault();
}