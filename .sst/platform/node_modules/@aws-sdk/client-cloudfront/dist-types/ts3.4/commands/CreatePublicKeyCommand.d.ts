import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  CreatePublicKeyRequest,
  CreatePublicKeyResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreatePublicKeyCommandInput extends CreatePublicKeyRequest {}
export interface CreatePublicKeyCommandOutput
  extends CreatePublicKeyResult,
    __MetadataBearer {}
export declare class CreatePublicKeyCommand extends $Command<
  CreatePublicKeyCommandInput,
  CreatePublicKeyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreatePublicKeyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreatePublicKeyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreatePublicKeyCommandInput, CreatePublicKeyCommandOutput>;
  private serialize;
  private deserialize;
}
