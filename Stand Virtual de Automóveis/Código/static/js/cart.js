var total =0;
$(' .price').each(function(){
    console.log(this);
  total += parseInt($(this).text());
});
$('.container').append("<div class='sum'>Total : "+total+"</div>");
console.log(total);