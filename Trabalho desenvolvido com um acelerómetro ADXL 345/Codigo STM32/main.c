/**
  ******************************************************************************
  * @file    main.c
  * @author  1181160@isep.ipp.pt && 1180919@isep.ipp.pt
  * @version V1.0
  * @date    04/11/2022 - 18/11/2022
  * @brief   SISTR Trabalho Intermedio
  ******************************************************************************
*/

// Bibliotecas

#include "stm32f10x.h"
#include "lcd.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Constantes
#define MSG_SIZE   30		//Tamanho max. vetor de mensagem
#define TEXT_SIZE  1		//Tamanho texto (normal) display
#define TITLE_SIZE 2		//Tamanho titulo display
#define X_COLUMN   3		//Coluna inicial texto display
#define GRAPH_LENGTH 120	//Comprimento (eixo t) dos gráficos do display

#define ERRO	   5		//Erro de leitura. Compara o valor lido com o valor médio dos últimos valores
							//se a diferença for inferior ao erro, o valor é adicionado à média, caso
							//contrário é iniciada uma nova média.

//Variaveis Globais
uint8_t  RxChar;			//Caracter recebido
uint8_t  NewMSG = 0;		//Flag de nova mensagem

uint8_t  x0;				//Guarda o valor do registo menos (0x32) significativo
uint8_t  x1;				//Guarda o valor do registo mais  (0x33) significativo
uint8_t	 x_cnt = 2;

int16_t  X;					//Valor já convertido para aceleração (m/s^2)
int16_t  X_Average 	= 0;

uint8_t  y0;
uint8_t  y1;
uint8_t	 y_cnt = 2;

int16_t  Y;
int16_t  Y_Average 	= 0;

uint8_t  z0;
uint8_t  z1;
uint8_t	 z_cnt = 2;

int16_t  Z;
int16_t  Z_Average	= 0;

uint8_t menu_select 	 = 1;
uint8_t menu_index  	 = 1;
uint8_t menu_index_old 	 = 0;

uint8_t input_delay_flag = 0;



/// Função Clock ------------------------------------------------------------------------------------------------------

void RCC_Config_HSE_PLL_Max()								//PLL 72 MHz --> (12 / 1) * 6
{
	RCC_HSEConfig(RCC_HSE_ON);					//Activa o HSE

	ErrorStatus HSEStartUpStatus;

	HSEStartUpStatus = RCC_WaitForHSEStartUp();

	if(HSEStartUpStatus == SUCCESS)				//Retorna SUCCESS ou ERROR
	{
		FLASH_SetLatency(FLASH_Latency_2);		//Define 2 wait states 48MHz <> 72MHz

		RCC_HCLKConfig(RCC_SYSCLK_Div1);		//Define AHB com prescaler de 1, logo 64MHz

		RCC_PCLK1Config(RCC_HCLK_Div2);			//Define APB1 com prescaler de 2, logo 36MHz

		RCC_PCLK2Config(RCC_HCLK_Div1);			//Define APB2 com prescaler de 1, logo 72MHz

		RCC_PLLConfig(							//Confi. PLL
					  RCC_PLLSource_HSE_Div1,	//Selecao sinal relogio (HSE) --> Opcao dividir por 1
					  RCC_PLLMul_6);			//Selecionar o prescaler do PLL para multiplicar por 6

		RCC_PLLCmd(ENABLE);						//Activa o PLL

		while(RCC_GetFlagStatus(RCC_FLAG_PLLRDY) == RESET); //Aguarda que o PLL inicie

		RCC_SYSCLKConfig(RCC_SYSCLKSource_PLLCLK); 			//Seleciona o PLL como fonte de relogio

		while(RCC_GetSYSCLKSource() != 0x08);				//Aguarda que a fonte escolhida seja a correta

		rcc_lcd_info();							//Display da conf. do relogio
	}
	else
		while(1); 								//ou iniciar um procedimento de erro
}


/// Funções GPIO ------------------------------------------------------------------------------------------------------

void init_GPIOB_AF()
{
	GPIO_InitTypeDef GPIO_InitStructure;

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_6;
	GPIO_InitStructure.GPIO_Speed 	= GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode 	= GPIO_Mode_AF_PP;

	GPIO_Init(GPIOB, &GPIO_InitStructure);
}

void init_GPIO_USART()
{
	GPIO_InitTypeDef GPIO_InitStructure;

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_2;										//TX
	GPIO_InitStructure.GPIO_Speed 	= GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode 	= GPIO_Mode_AF_PP;

	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_3;										//RX
	GPIO_InitStructure.GPIO_Speed 	= GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode 	= GPIO_Mode_IN_FLOATING;

	GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void init_GPIO_I2C()
{
	GPIO_InitTypeDef GPIO_InitStructure;

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_8 | GPIO_Pin_9;	//SCL - GPIOB8	| SDA -> GPIOB9
	GPIO_InitStructure.GPIO_Speed 	= GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode 	= GPIO_Mode_AF_OD;

	GPIO_Init(GPIOB, &GPIO_InitStructure);
}

void init_GPIO_Joystick()
{
	GPIO_InitTypeDef GPIO_InitStructure;

	GPIO_InitStructure.GPIO_Speed 	= GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode 	= GPIO_Mode_IPU;

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_1;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Pin 	= GPIO_Pin_3 | GPIO_Pin_2;
	GPIO_Init(GPIOC, &GPIO_InitStructure);
}


/// Funções TIM -------------------------------------------------------------------------------------------------------
void Set_TIM3(uint16_t ARR, uint16_t PSC)					 	//TIM3 - Usado para gerar um delay de 1s
{
	//Ativa o TIM3
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE );


	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;

	TIM_TimeBaseStructure.TIM_Period 		= ARR;			 	//auto-reload 0 a 65535

	TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;

	TIM_TimeBaseStructure.TIM_Prescaler 	= PSC; 			 	//prescaler de 0 a 65535

	TIM_TimeBaseStructure.TIM_CounterMode 	= TIM_CounterMode_Up;

	TIM_TimeBaseInit(TIM3, &TIM_TimeBaseStructure);

	//Inicia a contagem do TIM3
	TIM_Cmd(TIM3, ENABLE);
}

void Wait_TIM3_Flag()
{
	while(TIM_GetFlagStatus(TIM3,TIM_FLAG_Update) == RESET);//Aguarda pela flag de overflow do TIM3

	input_delay_flag = 0;									//Reinicia a flag do delay do input do utilisador

	TIM_ClearFlag(TIM3, TIM_FLAG_Update);					//Reinicia a flag para uma nova contagem
}

void Set_TIM4(uint16_t ARR, uint16_t PSC)					 	//TIM4 CounterMode_Up
{
	//Ativa o TIM4
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM4, ENABLE );


	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;

	TIM_TimeBaseStructure.TIM_Period 		= ARR;			 	//auto-reload 0 a 65535

	TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;

	TIM_TimeBaseStructure.TIM_Prescaler 	= PSC; 			 	//prescaler de 0 a 65535

	TIM_TimeBaseStructure.TIM_CounterMode 	= TIM_CounterMode_Up;

	TIM_TimeBaseInit(TIM4, &TIM_TimeBaseStructure);


	//Inicia a contagem do TIM4
	TIM_Cmd(TIM4, ENABLE);
}

void Conf_CH1_TM4_PWM2()										//TIM4 CH1 PWM2
{
	//Definição do canal 1 do TIM4 (GPIOB6)
	TIM_OCInitTypeDef TIM_OCInitStructure;

	TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM2;

	TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;

	TIM_OCInitStructure.TIM_Pulse = 0; /*0 a 65535*/

	TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_Low;

	TIM_OC1Init(TIM4, &TIM_OCInitStructure);
}


/// Funções USART -----------------------------------------------------------------------------------------------------
void Conf_NVIC_USART2(uint8_t p, uint8_t s)
{
	NVIC_InitTypeDef NVIC_InitStructure;

	NVIC_InitStructure.NVIC_IRQChannel = USART2_IRQn;

	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = p;

	NVIC_InitStructure.NVIC_IRQChannelSubPriority = s;

	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;

	NVIC_Init(&NVIC_InitStructure);
}

void init_usart(uint32_t baud)
{
	USART_InitTypeDef USART_InitStructure;

	USART_InitStructure.USART_BaudRate 				= baud;								//Velocidade de comunicacao
	USART_InitStructure.USART_WordLength 			= USART_WordLength_8b;				//Tamanho da mensagem transmitida (8bits)
	USART_InitStructure.USART_StopBits 				= USART_StopBits_1;					//1 stop bit
	USART_InitStructure.USART_Parity 				= USART_Parity_No;					//Sem paridade
	USART_InitStructure.USART_HardwareFlowControl 	= USART_HardwareFlowControl_None;	//Controlo por hardware
	USART_InitStructure.USART_Mode 					= USART_Mode_Tx | USART_Mode_Rx;	//Modo de escrita e leitura

	USART_Init(USART2, &USART_InitStructure);

	USART_Cmd(USART2, ENABLE);
}

void SendMSG_USART(uint8_t Data)
{
	while(USART_GetFlagStatus(USART2, USART_FLAG_TXE) == RESET);						//Esperar que o buffer esteja vazio

	USART_SendData(USART2, Data);														//Enviar os dados
}

uint8_t ReceiveMSG_USART()
{
	while(USART_GetFlagStatus(USART2, USART_FLAG_RXNE) == RESET );						//Esperar que cheguem dados à USART

	uint8_t RxData;
	RxData = USART_ReceiveData(USART2);													//Ler os dados da USART

	USART_ClearFlag(USART2,USART_FLAG_RXNE);											//Limpar a flag

	return RxData;
}


/// Funções I2C -------------------------------------------------------------------------------------------------------
void init_I2C()
{
	//Cortex Library pág. 184

	I2C_InitTypeDef I2C_InitStructure;

	I2C_InitStructure.I2C_Mode 					= I2C_Mode_I2C;						//Standard Mode
	I2C_InitStructure.I2C_DutyCycle 			= I2C_DutyCycle_2;
	I2C_InitStructure.I2C_Ack 					= I2C_Ack_Enable;
	I2C_InitStructure.I2C_AcknowledgedAddress 	= I2C_AcknowledgedAddress_7bit;
	I2C_InitStructure.I2C_ClockSpeed 			= 400000;							//400KHz

	I2C_Init(I2C1, &I2C_InitStructure);

	I2C_Cmd(I2C1, ENABLE);															//Ativa o periferico I2C1

	I2C_AcknowledgeConfig(I2C1, ENABLE);											//Ativa o Acknowledge do I2
}

void SendMSG_I2C(uint8_t addr, uint8_t data)
{
	while(I2C_GetFlagStatus(I2C1, I2C_FLAG_BUSY));							//Aguarda que o I2C esteja livre para a comunicação

	//START bit, sinaliza uma nova mensagem
	I2C_GenerateSTART(I2C1, ENABLE);
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT) != SUCCESS);

	//Slave Address + Write
	I2C_Send7bitAddress(I2C1, 0xA6, I2C_Direction_Transmitter);
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_TRANSMITTER_MODE_SELECTED) != SUCCESS);

	//Register Address
	I2C_SendData(I2C1, addr);												//addr - Endereço de escrita
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED) != SUCCESS);

	//Data Frame
	I2C_SendData(I2C1, data);												//data - Data a ser escrita no addr
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED) != SUCCESS);

	//STOP bit, fim da mensagem
	I2C_GenerateSTOP(I2C1, ENABLE);
}

void ReceiveMSG_I2C()
{
	I2C_AcknowledgeConfig(I2C1, ENABLE);									//Ativa o Acknowledge do I2C

	while(I2C_GetFlagStatus(I2C1, I2C_FLAG_BUSY));							//Aguarda que o I2C esteja livre para a comunicação

	//Construção da mensagem ------------------------------------------------------------

	//START bit, sinaliza uma nova mensagem
	I2C_GenerateSTART(I2C1, ENABLE);
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT) != SUCCESS);

	//Slave Address + Write
	I2C_Send7bitAddress(I2C1, 0xA6, I2C_Direction_Transmitter);				//0xA6 - Endereço alternativo de escrita
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_TRANSMITTER_MODE_SELECTED) != SUCCESS);

	//Register Address
	I2C_SendData(I2C1, 0x32);												//0x32 - 1º endereço de registo (Data x0)
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_TRANSMITTED) != SUCCESS);

	//Segundo START bit, funciona como um RESTART ou um STOP seguido de um START
	I2C_GenerateSTART(I2C1, ENABLE);
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_MODE_SELECT) != SUCCESS);

	//Slave Address + Read
	I2C_Send7bitAddress(I2C1, 0xA7, I2C_Direction_Receiver);				//0xA7 - Endereço alternativo de leitura
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_RECEIVER_MODE_SELECTED) != SUCCESS);


	//Eixo X ----------------------------------------------------------------------------
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 1, 8bits menos significativos do X
	x0 = I2C_ReceiveData(I2C1);												//Leitura dos 8bits menos significativos do eixo X

	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 2, 8bits mais significativos do X
	x1 = I2C_ReceiveData(I2C1);												//Leitura dos 8bits mais significativos do eixo X

	X = ((x1 << 8) + x0);													//X = shift de 8bits de x1 + x0
	X = (X  * 0.0039 * 9.81) * 100;											//Conversão de força (g) em aceleração (m/s^2)
																			//Multiplica por 100 para transformar o float num int

	if(abs(X - X_Average) < ERRO)											//Calculo da media dos valores lidos no eixo X
																			//Se a diferença entre o último valor de X e o atual for inferior ao ERRO,
		X_Average = (X_Average + X) /2;										//a medição é considerada como ruido e o valor retornado é o valor médio das 2 leituras.
	else
		X_Average = X;														//Caso contrário é retornado o valor da medição atual.


	//Eixo Y ----------------------------------------------------------------------------
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 3
	y0 = I2C_ReceiveData(I2C1);

	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 4
	y1 = I2C_ReceiveData(I2C1);

	Y = ((y1 << 8) + y0) ;
	Y = (Y  * 0.0039 * 9.81) * 100;

	if(abs(Y - Y_Average) < ERRO)
		Y_Average = (Y_Average + Y) /2;
	else
		Y_Average = Y;


	//Eixo Z ----------------------------------------------------------------------------
	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 5
	z0 = I2C_ReceiveData(I2C1);

	while(I2C_CheckEvent(I2C1, I2C_EVENT_MASTER_BYTE_RECEIVED) != SUCCESS);	//Data Frame 6
	z1 = I2C_ReceiveData(I2C1);

	Z = ((z1 << 8) + z0);
	Z = (Z  * 0.0039 * 9.81) * 100;

	if(abs(Z - 	Z_Average) < ERRO)
		Z_Average = (Z_Average + Z) /2;
	else
		Z_Average = Z;

	//Fim da Mensagem -------------------------------------------------------------------
	I2C_AcknowledgeConfig(I2C1, DISABLE);									//Desablita o Acknowledge do I2C
	I2C_GenerateSTOP(I2C1, ENABLE);											//Gera um STOP bit que sinaliza o fim da mensagem
}


/// Joystick ----------------------------------------------------------------------------------------------------------
void Conf_NVIC_Joystick()
{
	NVIC_InitTypeDef NVIC_InitStructure;

	//Interrupção global do GPIOS A1, C2 e C3 com prioridade 0 e sub-prioridade 0

	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0;

	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;

	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;


	NVIC_InitStructure.NVIC_IRQChannel = EXTI1_IRQn;
	NVIC_Init(&NVIC_InitStructure);

	NVIC_InitStructure.NVIC_IRQChannel = EXTI2_IRQn;
	NVIC_Init(&NVIC_InitStructure);

	NVIC_InitStructure.NVIC_IRQChannel = EXTI3_IRQn;
	NVIC_Init(&NVIC_InitStructure);
}

void Conf_EXTI()
{
	GPIO_EXTILineConfig(GPIO_PortSourceGPIOA, GPIO_PinSource1);		//Set da interrupção do GPIOA1
	GPIO_EXTILineConfig(GPIO_PortSourceGPIOC, GPIO_PinSource2);		//Set da interrupção do GPIOC2
	GPIO_EXTILineConfig(GPIO_PortSourceGPIOC, GPIO_PinSource3);		//Set da interrupção do GPIOC3

	EXTI_InitTypeDef EXTI_InitStructure;

	RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE);			//Ativar o clock AFIO para o uso do EXTI

	EXTI_InitStructure.EXTI_Line = EXTI_Line1 | EXTI_Line2 | EXTI_Line3;

	EXTI_InitStructure.EXTI_Mode = EXTI_Mode_Interrupt;

	EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Falling;

	EXTI_InitStructure.EXTI_LineCmd = ENABLE;

	EXTI_Init(&EXTI_InitStructure);
}


/// Funções Display ---------------------------------------------------------------------------------------------------
void Display_Window_Preset(char *msg)
{
	lcd_draw_string(X_COLUMN, 0, msg, 0, TITLE_SIZE);

	sprintf(msg,"<Press ENTER>");
	lcd_draw_string(47, 55, msg, 0, TEXT_SIZE);
}

void Display_Axis()
{
	lcd_draw_line(1,16, 1,55, WHITE); 	//Eixo x(t)
	lcd_draw_line(1,36, GRAPH_LENGTH,36, WHITE);	//Eixo Tempo

	lcd_draw_char(120, 36, 't', 1, 1);

}

void Display_Data(int16_t data, uint8_t cnt)
{
	int16_t aux = data / 100;

	//Display
	lcd_draw_fillrect(cnt, 16, 5, 39, BLACK);		//Apaga os dados antigos (5 pixeis à frente do atual)

	Display_Axis();

	lcd_draw_pixel(cnt, 36 - aux, 1);				//Desenha um novo ponto

	//LED Auxiliar
	if(aux < 0)										//Acelerações inferiores a 0, LED desligado
		aux = 0;
	else if(aux > 198)								//Acelerações superiores ao auto-reload, LED máximo
		aux = 198;

	TIM_SetCompare1(TIM4, aux);						//Varia a intencidade do LED consuante o valor no eixo especificado
}

/// Função Inicialização ----------------------------------------------------------------------------------------------

void init()
{
	//Set clock to 72MHz
	RCC_Config_HSE_PLL_Max();

	//Enable USART e I2C
	RCC_APB1PeriphClockCmd( RCC_APB1Periph_USART2 |
						    RCC_APB1Periph_I2C1	  , ENABLE);

	//Enable GPIOA, B e C, e AFIO
	RCC_APB2PeriphClockCmd( RCC_APB2Periph_GPIOA |
							RCC_APB2Periph_GPIOB |
							RCC_APB2Periph_GPIOC |
							RCC_APB2Periph_AFIO  , ENABLE);

	//REMAP I2C
	GPIO_PinRemapConfig(GPIO_Remap_I2C1, ENABLE);

	//Set Interrupt priority group
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_4);				//Apenas usa o grupo de superioridade
																//Apenas Conf. 1 vez

	//Init display
	lcd_init();


	//Init I2C
	init_GPIO_I2C();											//Configuração do GPIO do I2C
	init_I2C();													//Inicialização do I2C


	// Configuração dos registos do acelerometro
	SendMSG_I2C(0x2D, 0b00001000); 								//ADXL345 - measure mode
	SendMSG_I2C(0x31, 0b00001000);								//ADXL345 - data-format


	//Init USART
	init_GPIO_USART();
	init_usart(9600);
	Conf_NVIC_USART2(0, 0);
	USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);				//Ativa a interrupção de receção


	//Init TIM
	Set_TIM3(1999, 35999);										//Configuração do TIM3 para 1s

	init_GPIOB_AF();											//Configuração do LED do PWM
	Set_TIM4(199, 359);											//Configuração TIM4
	Conf_CH1_TM4_PWM2();										//Configuração do PWM


	//Init Joystick
	init_GPIO_Joystick();										//Configuração do GPIO
	Conf_NVIC_Joystick();										//Configuração do NVIC
	Conf_EXTI();												//Configuração do EXTI

}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/// Funcionamento -----------------------------------------------------------------------------------------------------
void menu()
{
	char msg[MSG_SIZE];

	if(menu_index != menu_index_old || menu_index == 0)
	{
		lcd_draw_fillrect(0, 0, 128, 64, BLACK);
		menu_index_old = menu_index;

		TIM_SetCompare1(TIM4, 0);						//Reset PWM

		x_cnt = 2;										//Reset
		y_cnt = 2;
		z_cnt = 2;
	}

	switch(menu_index)
	{
		case 0:						//Menu
			sprintf(msg,"Menu");
			lcd_draw_string(X_COLUMN, 0, msg, 0, TITLE_SIZE);

			sprintf(msg,"Pagina Inicial");
			lcd_draw_string(X_COLUMN, 17, msg, 0, TEXT_SIZE);

			sprintf(msg,"Grafico X");
			lcd_draw_string(X_COLUMN, 26, msg, 0, TEXT_SIZE);

			sprintf(msg,"Grafico Y");
			lcd_draw_string(X_COLUMN, 35, msg, 0, TEXT_SIZE);

			sprintf(msg,"Grafico Z");
			lcd_draw_string(X_COLUMN, 44, msg, 0, TEXT_SIZE);

			sprintf(msg,"Computador");
			lcd_draw_string(X_COLUMN, 53, msg, 0, TEXT_SIZE);

			lcd_draw_rect(1, 16 + (menu_select - 1) * 9, 126, 8, 1);

			break;

		case 1:						//Ecrã inicial
			sprintf(msg,"SISTR 2022");
			lcd_draw_string(X_COLUMN, 0, msg, 0, TITLE_SIZE);

			sprintf(msg,"<Press ENTER>");
			lcd_draw_string(23, 31, msg, 0, TEXT_SIZE);

			sprintf(msg,"1180919 Diogo Freitas");
			lcd_draw_string(1, 47, msg, 0, TEXT_SIZE);

			sprintf(msg,"1181160 Manuel Couto");
			lcd_draw_string(1, 55, msg, 0, TEXT_SIZE);
			break;

		case 2:						//Gráfico X
			sprintf(msg,"Grafico X");
			Display_Window_Preset(msg);

			Display_Data(X_Average, x_cnt);

			if(x_cnt < GRAPH_LENGTH)
				x_cnt++;
			else
				x_cnt = 2;
			break;

		case 3:						//Gráfico Y
			sprintf(msg,"Grafico Y");
			Display_Window_Preset(msg);

			Display_Data(Y_Average, y_cnt);

			if(y_cnt < GRAPH_LENGTH)
				y_cnt++;
			else
				y_cnt = 2;
			break;

		case 4:						//Gráfico Z
			sprintf(msg,"Grafico Z");
			Display_Window_Preset(msg);

			Display_Data(Z_Average, z_cnt);
			if(z_cnt < GRAPH_LENGTH)
				z_cnt++;
			else
				z_cnt = 2;
			break;

		case 5:						//Pc
			sprintf(msg,"Computador");
			Display_Window_Preset(msg);

			sprintf(msg,"Abra o Unity / Porta");
			lcd_draw_string(X_COLUMN, 16, msg, 0, TEXT_SIZE);

			sprintf(msg,"Serie. Incline o");
			lcd_draw_string(X_COLUMN, 25, msg, 0, TEXT_SIZE);

			sprintf(msg,"Micro para controlar");
			lcd_draw_string(X_COLUMN, 34, msg, 0, TEXT_SIZE);

			sprintf(msg,"o submarino.");
			lcd_draw_string(X_COLUMN, 43, msg, 0, TEXT_SIZE);

			//Unity
			sprintf(msg,"%d,%d", X_Average, Y_Average);

			//Serial Port
			//sprintf(msg,"X: %d\t Y: %d\t Z: %d\n", X_Average, Y_Average, Z_Average);

			for(int i=0;i<MSG_SIZE;i++)
			{
				SendMSG_USART(msg[i]);

				if (msg[i] == '\0') break;
			}
			break;

		default:
			break;
	}

	display();
}

int main()
{
	init();

	while(1)
	{
		ReceiveMSG_I2C();			//lê valores do sensor

		menu();

		Wait_TIM3_Flag();
	}
}
