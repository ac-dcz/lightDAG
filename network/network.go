package network

import (
	"encoding/gob"
	"io"
	"lightDAG/logger"
	"net"
)

type NetMessage struct {
	Msg     *Messgae
	Address string
}

type Messgae struct {
	From int
	Typ  int
	Data []byte
}

type Sender struct {
	msgCh chan *NetMessage
	conns map[string]chan<- *Messgae
}

func NewSender() *Sender {
	sender := &Sender{
		msgCh: make(chan *NetMessage, 1000),
		conns: make(map[string]chan<- *Messgae),
	}
	return sender
}

func (s *Sender) Run() {
	for msg := range s.msgCh {
		if conn, ok := s.conns[msg.Address]; ok {
			conn <- msg.Msg
		} else {
			conn, err := s.connect(msg.Address)
			if err != nil {
				continue
			} else {
				s.conns[msg.Address] = conn
				conn <- msg.Msg
			}
		}
	}
}

func (s *Sender) Send(msg *NetMessage) {
	s.msgCh <- msg
}

func (s *Sender) SendChannel() chan<- *NetMessage {
	return s.msgCh
}

func (s *Sender) connect(addr string) (chan<- *Messgae, error) {
	msgCh := make(chan *Messgae, 1000)
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		logger.Warn.Printf("Failed to connect to %s: %v \n", addr, err)
		return nil, err
	}
	logger.Info.Printf("Outgoing connection established with %s \n", addr)
	go func() {
		encoder := gob.NewEncoder(conn)
		for msg := range msgCh {
			if err := encoder.Encode(msg); err != nil {
				logger.Warn.Printf("Failed to send message to %s: %v \n", addr, err)
			} else {
				logger.Debug.Printf("Successfully sent message to %s \n", addr)
			}
		}
	}()
	return msgCh, nil
}

type Receiver struct {
	addr string
	msg  chan *Messgae
}

func NewReceiver(addr string) *Receiver {

	receiver := &Receiver{
		addr: addr,
		msg:  make(chan *Messgae, 1000),
	}

	return receiver
}

func (recv *Receiver) Run() {
	listen, err := net.Listen("tcp", recv.addr)
	if err != nil {
		logger.Error.Printf("Failed to bind to TCP addr : %s \n", err)
		panic(err)
	}
	logger.Debug.Printf("Listening on %s \n", recv.addr)

	for {
		conn, err := listen.Accept()
		if err != nil {
			logger.Warn.Printf("Failed to accept : %v \n", err)
			continue
		}
		logger.Info.Printf("Incoming connection established with %v \n", conn.RemoteAddr())
		go recv.serveConn(conn)
	}
}

func (recv *Receiver) serveConn(conn net.Conn) {
	decoder := gob.NewDecoder(conn)
	for {
		msg := &Messgae{}
		if err := decoder.Decode(msg); err != nil {
			// logger.Debug.Printf("Received %v", msg)
			if err != io.EOF {
				logger.Warn.Printf("failed to receive : %v \n", err)
			}
			return
		}
		recv.msg <- msg
	}
}

func (recv *Receiver) Recv() *Messgae {
	return <-recv.msg
}

func (recv *Receiver) RecvChannel() <-chan *Messgae {
	return recv.msg
}
