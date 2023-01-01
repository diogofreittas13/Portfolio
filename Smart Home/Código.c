/*
 * Smart Home
 *
 * Created: 15/10/2020 12:05:46
 * Author : 
 Tiago Machado – 1171126
 Diogo Freitas – 1180919

 */ 
#define F_CPU   1000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdlib.h>
#include <string.h>

#define LCD_Dir  DDRB			/* Define LCD data port direction */
#define LCD_Port PORTB			/* Define LCD data port */
#define RS PB0				/* Define Register Select pin */
#define EN PB1 			/* Define Enable signal pin */



#define  Led_Pisca PD4 // vermelho_pisca
/*#define  Azul   PD0 // azul
  #define  Rosa   PD1 // rosa
  #define  Amarelo   PD2 // amarelo
  #define  Laranja   PD3 // laranja*/

const unsigned char step_motor[] = {0b00000011,0b00000110,0b00001100,0b00001001}; // tabela para rodar o motor
unsigned char intensidade_luz_ext; // exterior
unsigned char intensidade_luz_int; // interior 

unsigned char passo_esquerda_abrir=4, passo_direita_fechar=0;
//unsigned char estado_estore=0;; // 0-fechado 1-aberto
unsigned int teste;

/********************************************************************************
						Inicialization & Timer SECTION
*********************************************************************************/

void init()
	{
/* Inicialização dos portes para o motor,pisca e lcd*/
		
		DDRB = 0xff;// todo como saida para o lcd
		DDRD = 0b01011111;  // bit 0,1,2,3 para step-motor , bit 4 como led_pisca e bit 6 como led interior
			
 /*timer1_init*/
 
	    // CTC timer com 500ms de tempo base
		TCNT0= 0x00; // garantir que começa a 0
		TCCR1B |= (1 << WGM12) | (1<<CS12); // Modo 4 CTC com prescaler de 256
		TIMSK1 |= (1 << OCIE1A); // ativar as interrupções
		OCR1A = 1953; // OCR1A = (F_CPU/freq*256)-1 , visto que tamos no timer 1 de 16bits o valor de OCR1 pode ir até aos 65356 - Freq = 2hz OCR1A = (1000000/2*256)-1 = 1953
	
 /*timer0_init*/ // alterar para o timer 0 para colocar os leds

		TCNT0 = 0x00; // garantir que começa a 0
		TCCR0A |= (1 << WGM00) | (1 << WGM01) | (1 << COM0A1); // Modo Fast PWM e non-inverting e clear on compare match
		TCCR0B |= (1 << CS00); // sem prescaler
		OCR0A = 0; // começa desligado
	
/*adc_inicio*/
	
	    ADMUX |= (1 << REFS0) | (1 << ADLAR)| (1<<MUX0); //| (1<<MUX1) //// ajustado a esquerda porque só tem 8 bits e condensador a entrada e channel 0
		ADCSRA |= (1 << ADEN) | (1 <<ADPS2) | (1<< ADIE) ;  // fator de 16 e adlar ativo -> freq = Freq_CPU / divisor -- freq = 1000000/16 = 62500 hz. Tem de estar entre 50khz e 200khz
				
	    sei();       // ativar as interrupções no sreg
	
	   ADCSRA |= 1<<ADSC; //começa a fazer a conversão
	}
	
/********************************************************************************
							Led_Piscar
********************************************************************************/
								
ISR (TIMER1_COMPA_vect)
	{
		PORTD ^= (1 << Led_Pisca); // altera o bit 0 do portb de 0 - 1 e de 1-0
	}


/********************************************************************************
						ADC SECTION
*********************************************************************************/

ISR(ADC_vect)
{
	uint8_t Valores = ADCH;
	uint16_t lux;
	
	switch(ADMUX) // ve o canal em que está ou no canal 1 ou no canal 2
	{
			case(0x61): // canal 1
				lux= Valores;
				intensidade_luz_ext = (lux*100)/256;  //como esta esquerda com 8 bit basta ler o valor de adch -  transforma o valor lido de 0-100%
				ADMUX = 0x62; // troca para o canal 2
				break;
				
			case(0x62): // canal 2
				lux = Valores;
				intensidade_luz_int = (lux*100)/256; //como esta esquerda com 8 bit basta ler o valor de adch -  transforma o valor lido de 0-100%
				ADMUX = 0x61; // troca para o canal 1
				break;
				
			default:
				break;
	}
	ADCSRA |= 1<<ADSC; // inicia a conversação
}


/********************************************************************************
						LCD SECTION
*********************************************************************************/

void LCD_Command( unsigned char cmnd )
{
	LCD_Port = (LCD_Port & 0x0F) | (cmnd & 0xF0); /* sending upper nibble */
	LCD_Port &= ~ (1<<RS);		/* RS=0, command reg. */
	LCD_Port |= (1<<EN);		/* Enable pulse */
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);

	_delay_us(200);

	LCD_Port = (LCD_Port & 0x0F) | (cmnd << 4);  /* sending lower nibble */
	LCD_Port |= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_ms(2);
}


void LCD_Char( unsigned char data )
{
	LCD_Port = (LCD_Port & 0x0F) | (data & 0xF0); /* sending upper nibble */
	LCD_Port |= (1<<RS);		/* RS=1, data reg. */
	LCD_Port|= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);

	_delay_us(200);

	LCD_Port = (LCD_Port & 0x0F) | (data << 4); /* sending lower nibble */
	LCD_Port |= (1<<EN);
	_delay_us(1);
	LCD_Port &= ~ (1<<EN);
	_delay_ms(2);
}

void LCD_Init (void)			/* LCD Initialize function */
{
	LCD_Dir = 0xFF;			/* Make LCD port direction as o/p */
	_delay_ms(20);			/* LCD Power ON delay always >15ms */
	
	LCD_Command(0x02);		/* send for 4 bit initialization of LCD  */
	LCD_Command(0x28);              /* 2 line, 5*7 matrix in 4-bit mode */
	LCD_Command(0x0c);              /* Display on cursor off*/
	LCD_Command(0x06);              /* Increment cursor (shift cursor to right)*/
	LCD_Command(0x01);              /* Clear display screen*/
	_delay_ms(2);
}


void LCD_String (char *str)		/* Send string to LCD function */
{
	int i;
	for(i=0;str[i]!=0;i++)		/* Send each char of string till the NULL */
	{
		LCD_Char (str[i]);
	}
}

void LCD_String_xy (char row, char pos, char *str)	/* Send string to LCD with xy position */
{
	if (row == 0 && pos<16)
	LCD_Command((pos & 0x0F)|0x80);	/* Command of first row and required position<16 */
	else if (row == 1 && pos<16)
	LCD_Command((pos & 0x0F)|0xC0);	/* Command of first row and required position<16 */
	LCD_String(str);		/* Call LCD string function */
}

void LCD_Clear()
{
	LCD_Command (0x01);		/* Clear display */
	_delay_ms(2);
	LCD_Command (0x80);		/* Cursor at home position */
}


void update_LCD()
{
	char string[4];
	char string_2[4];
	itoa(intensidade_luz_ext, string, 10); //converte o valor númerico numa string para ser utilizada no lcd
	itoa(intensidade_luz_int,string_2,10);
	LCD_String_xy(0,4,string); // seleciona a linha de cima e a posição 4 para escrever
	LCD_String_xy(1,4,string_2); // seleciona a segunda linha e a posição 4 para escrever
}

/********************************************************************************
						Motor SECTION
*********************************************************************************/

void incrementa_fullstep_fechar()
{
	if (passo_direita_fechar != 4){
		PORTD=step_motor[passo_direita_fechar]; //envia para o motor a sequência de bits correspondentes a posição do array "step_motor[]"
		passo_direita_fechar ++; //incrementa a variável para avançar uma posição no array
		_delay_ms(5); // espera 5ms antes de continuar
	}
	if (passo_direita_fechar == 4 ) // ve se já percorreu todas as posição do array
	passo_direita_fechar = 0 ; // se sim, volta a posição 0
	
}

void decrementar_fullstep_abrir()
{
    // o mesmo processo que o "incrementa_fullstep_fechar()" só que ao contrário, começa pela última posição e vai percorrendo o array ao contrário para ele virar em sentido oposto
	if (passo_esquerda_abrir != 0){ 
		passo_esquerda_abrir --;
		PORTD=step_motor[passo_esquerda_abrir];
		_delay_ms(5);
	}
	if (passo_esquerda_abrir == 0)
	passo_esquerda_abrir=4;
	
}

/********************************************************************************
						Main SECTION
*********************************************************************************/
	
int main(void)
{
    init();		  /* Initialization dos PORTS,ADC,MOTOR,PISCA,TIMER */ 	
	LCD_Init();	  /* Initialization of LCD */
	
	
	LCD_Clear();  // Limpa o LCD de qualquer valor
	LCD_String("Ext:"); //Coloca a palavra 'EXT' na linha 0 - Significa Exterior
	LCD_Command(0xC0);  // Avança o curso do LCD para a linha 1
	LCD_String("Int:"); //Coloca a palavra 'INT' na linha 0 - Significa Interior
	LCD_String_xy(0,6,"%"); //Coloca % na linha 0 e no 6 espaço
	LCD_String_xy(1,6,"%"); //Coloca % na linha 0 e no 6 espaço
	
	unsigned char state_estore=0; // 0- fechado \ 1 - aberto
	unsigned int rotacao=0; // nº de voltas para rodar
	
    while (1) 
    {  
		
		update_LCD();
		if (state_estore == 0) // verifica o estado do estore = 0 (fechado)
			{
				if (intensidade_luz_ext > 35) // se o state_estore estiver fechado e a intensidade da luz exterior for superior a 35% o estore vai abrir
					{
						while (rotacao < 1050) // numero de passos a efetuar para abrir o estore
							{
								incrementa_fullstep_fechar(); // chama a função para comunicar com o motor
								LCD_String_xy(0,8,"Abrindo"); //coloca no lcd "abrindo" durante o processo
								rotacao++;					// incrementa a rotação		
							}
						LCD_String_xy(0,8,"Aberto"); // coloca no lcd "aberto"
						LCD_String_xy(0,14,"  ");
						state_estore=1; // Coloca a veriavel state_estore a =1 para indicar que está aberto e o motor não entrar no ciclo outra vez.
						rotacao=0; // coloca a variavel rotação a 0 para se conseguir utilizar noutro ciclo novamente
					}	
			}
		if (state_estore==1) // verifica o estado do estore = 1 (abrir)
			{
				if (intensidade_luz_ext <35) // se o state_estore estiver aberto e a intensidade da luz exterior for inferior a 35% o estore vai fechar
					{
						while (rotacao <1050) // numero de passos a efetuar para fechar o estore
							{
								decrementar_fullstep_abrir(); // chama a função para comunicar com o motor
								LCD_String_xy(0,8,"Fechando"); //coloca no lcd "fechando" durante o processo
								rotacao++;						// incrementa a rotação
							}
						LCD_String_xy(0,8,"Fechado"); // coloca no lcd "fechado"
						LCD_String_xy(0,16," ");
						state_estore=0; // Coloca a veriavel state_estore a =0 para indicar que está fechado e o motor não entrar no ciclo outra vez.
						rotacao=0; // coloca a variavel rotação a 0 para se conseguir utilizar noutro ciclo novamente
					}
			}
		
		if (intensidade_luz_int<55){ //  entre 55 e 65 % intensidade interior	
			OCR0A = (100*255)/100; // a luz no interior 100%
			LCD_String_xy(1,8,"Luz On "); // coloca no lcd que a luz está ligada
		}
		
		if ((intensidade_luz_int>55) && (intensidade_luz_int<65)){//  entre 55 e 65 % intensidade interior
			OCR0A = (50*255)/100; // a luz no interior 50%
			LCD_String_xy(1,8,"Luz 50%"); // coloca no lcd que a luz está a 50%
		}
		
		if (intensidade_luz_int> 65){
			OCR0A=0; // desligar luz no interior para uma intensidade superior a 65%	
			LCD_String_xy(1,8,"Luz Off"); //Coloca no lcd que a luz está desligada
		}
		_delay_ms(50); // espera 50ms para voltar a repetir o programa
    }
}



/* Cálculos das resistências
 
	como são 2 leds vermelhos os valores são os mesmos:
	- IF = 20 mA ; VF = 1.8 ; Rled = V-Vf/If
      Rled = 5-1.8 / 0.02 =160 ? ? 220 ?1 -> 220 ohms é o valor mais próximo.	  sensor (5V) + 10k resistencia (GND) -> tensão no ponto médio	  Quando está tudo claro valor lido é máximo 256 o que equivale a 5V e a resistencia é minima. Se estiver escuro a resistencia é máxima, o valor lido é 0 e a tensão será de 0V	  	  Regra de 3 simples traduzimos o valor lido do ad para intensidade 0-100%	  */



